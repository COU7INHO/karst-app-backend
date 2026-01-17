import re
import os
import base64
import logging
from typing import Dict
from datetime import timedelta
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def parse_time_to_duration(time_str: str) -> timedelta:
    """Convert time string (e.g. '0:36.776') to timedelta."""
    try:
        time_str = time_str.strip().replace(' ', '')
        match = re.match(r'(\d+):(\d+)\.(\d+)', time_str)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            milliseconds = int(match.group(3))
            return timedelta(minutes=minutes, seconds=seconds, milliseconds=milliseconds)
    except Exception:
        pass
    return None


def extract_race_data_from_image(image_file) -> Dict:
    """
    Extract race data from image using Mistral OCR.

    Returns dict with drivers list containing name, laps, fastest and average lap times.
    """
    logger.info("Reading and encoding image...")
    # Read and encode image
    image_file.seek(0)
    image_bytes = image_file.read()
    image_size_kb = len(image_bytes) / 1024
    logger.info(f"Image size: {image_size_kb:.2f} KB")

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    logger.info(f"Base64 encoded image length: {len(base64_image)} chars")

    # Prompt for Mistral
    prompt = """
    Extract race results from this karting timing sheet.

    TABLE STRUCTURE:
    - First column: Lap numbers (1, 2, 3, ...)
    - Remaining columns: One column per driver with their lap times
    - Header row: Driver names (e.g., Tiago, Gonçalo, Pedro Vil, Diogo, Mestre, Soham, Plata, Mota)
    - Bottom section: "M. Volta" (fastest lap) and "Média" (average lap) for each driver

    TIME FORMAT (CRITICAL - READ CAREFULLY):
    Lap times can be in these formats:
    - 0:36.776 (0 minutes, 36.776 seconds)
    - 0:41.609 (0 minutes, 41.609 seconds)
    - 1:23.456 (1 minute, 23.456 seconds)
    - 01:23.456 (same as above - 1 minute, 23.456 seconds)
    - 12:34.567 (12 minutes, 34.567 seconds)

    ⚠️ CRITICAL TIME READING RULES:
    1. Read ALL digits before the colon (:) - this is the MINUTES
       - "0:41.609" = 0 minutes (NOT 1 minute!)
       - "1:41.609" = 1 minute (NOT 0 minutes!)
       - "01:41.609" = 1 minute (leading zero can be present or absent)
    2. If the minutes digit is partially obscured or unclear, look at the context:
       - Lap times are usually 35-50 seconds (0:35 to 0:50)
       - Times over 1 minute are RARE but possible
       - If you see "?:41.609" where ? is unclear, it's most likely "1:41.609" NOT "0:41.609"
    3. Read ALL THREE digits after the decimal point (milliseconds)
    4. NEVER truncate or drop leading digits

    CRITICAL COLUMN ALIGNMENT RULES:
    1. First, identify ALL driver names in the header row from left to right
    2. For each row, read lap times STRICTLY in the same column order as the driver names
    3. DO NOT mix up columns - lap time in column 2 belongs to driver in position 2, etc.
    4. If a cell is EMPTY, BLANK, or contains a dash (-), DO NOT include that lap for that driver
    5. STOP reading laps for a driver when you encounter an empty cell for that driver
    6. NOT ALL DRIVERS complete the same number of laps - this is NORMAL and EXPECTED

    EXAMPLE CORRECT READING:
    Header: Tiago | Gonçalo | Rui
    Row 1:  0:40.123 | 0:39.456  | 1:41.789  → Tiago lap 1 = 0:40.123, Gonçalo lap 1 = 0:39.456, Rui lap 1 = 1:41.789
    Row 2:  0:39.876 | 0:38.901  | (empty)   → Tiago lap 2 = 0:39.876, Gonçalo lap 2 = 0:38.901, Rui has NO lap 2
    Row 3:  (empty)  | 1:39.111  | (empty)   → Tiago has NO lap 3, Gonçalo lap 3 = 1:39.111, Rui has NO lap 3

    FORBIDDEN ERRORS TO AVOID:
    - ❌ DO NOT drop leading digits (1:41.609 becoming 0:41.609)
    - ❌ DO NOT assign a time from column 5 to the driver in column 3
    - ❌ DO NOT continue reading laps after encountering an empty cell for that driver
    - ❌ DO NOT invent or duplicate lap times
    - ❌ DO NOT skip drivers - include ALL drivers from the header row
    - ❌ DO NOT truncate milliseconds (0:36.776 NOT 0:36.77)

    Return ONLY valid JSON in this exact format:
    {
        "drivers": [
            {
                "name": "Driver Name",
                "laps": [
                    {"lap_number": 1, "lap_time": "0:36.776"},
                    {"lap_number": 2, "lap_time": "1:23.854"}
                ],
                "fastest_lap": "0:35.703",
                "average_lap": "0:36.323"
            }
        ]
    }

    No additional text, only JSON.
    """

    logger.info("Calling Mistral API with pixtral-12b-2409 model...")

    try:
        response = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                    ]
                }
            ]
        )

        logger.info("Mistral API response received")
        logger.debug(f"Response object: {response}")

        # Parse response
        import json
        result_text = response.choices[0].message.content
        logger.info(f"Raw response length: {len(result_text)} chars")
        logger.debug(f"Raw response text: {result_text[:500]}...")

        # Extract JSON from response (in case there's extra text)
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
            logger.info("Extracted JSON from response")
        else:
            logger.warning("No JSON pattern found in response, using raw text")

        logger.info("Parsing JSON response...")
        result = json.loads(result_text)

        driver_count = len(result.get('drivers', []))
        logger.info(f"Successfully parsed JSON: {driver_count} drivers found")

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {result_text}")
        raise Exception(f"Invalid JSON response from OCR: {e}")

    except Exception as e:
        logger.error(f"Mistral API call failed: {e}", exc_info=True)
        raise
