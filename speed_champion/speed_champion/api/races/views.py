from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Min, Avg
from datetime import datetime, timedelta
import logging
from .serializers import (
    OCRUploadSerializer,
    SaveRaceResultSerializer,
    RaceListSerializer,
    RaceDetailSerializer
)
from .ocr_parser import extract_race_data_from_image, parse_time_to_duration
from .models import Race, RaceResult, LapTime
from ..drivers.models import Driver
from ..circuits.models import Circuit

logger = logging.getLogger(__name__)


def format_duration(duration):
    """Format timedelta to M:SS.mmm"""
    if not duration:
        return None
    total_seconds = duration.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds % 1) * 1000)
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}"


class UploadRaceImageView(APIView):
    """Upload race result image and extract data via OCR."""

    def post(self, request):
        logger.info("=== OCR Upload Started ===")

        serializer = OCRUploadSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image = serializer.validated_data['image']
        logger.info(f"Image received: name={image.name}, size={image.size} bytes")

        try:
            logger.info("Starting OCR extraction with Mistral...")
            result = extract_race_data_from_image(image)

            driver_count = len(result.get('drivers', []))
            logger.info(f"OCR extraction successful: {driver_count} drivers detected")

            for idx, driver in enumerate(result.get('drivers', []), 1):
                logger.info(f"  Driver {idx}: {driver.get('name')} - {len(driver.get('laps', []))} laps")

            logger.info("=== OCR Upload Completed Successfully ===")
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"OCR extraction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListRacesView(APIView):
    """List all races, optionally filter by circuit or driver."""

    def get(self, request):
        races = Race.objects.all()

        # Filter by circuit if provided
        circuit_id = request.query_params.get('circuit')
        if circuit_id:
            try:
                circuit_id = int(circuit_id)
                races = races.filter(circuit_id=circuit_id)
            except ValueError:
                return Response(
                    {"error": "Invalid circuit ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Filter by driver if provided (accept both 'driver' and 'drivers')
        driver_id = request.query_params.get('driver') or request.query_params.get('drivers')
        if driver_id:
            try:
                driver_id = int(driver_id)
                races = races.filter(raceresult__driver_id=driver_id).distinct()
            except ValueError:
                return Response(
                    {"error": "Invalid driver ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        races = races.order_by('-date')
        serializer = RaceListSerializer(races, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RaceDetailView(APIView):
    """Get race details with results."""

    def get(self, request, race_id):
        try:
            race = Race.objects.get(id=race_id)
        except Race.DoesNotExist:
            return Response(
                {"error": "Race not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RaceDetailSerializer(race)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SaveRaceResultsView(APIView):
    """Save race results with selected drivers."""

    def post(self, request):
        logger.info("=== Save Race Results Started ===")

        serializer = SaveRaceResultSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        circuit = Circuit.objects.get(id=serializer.validated_data['circuit_id'])
        date = serializer.validated_data['date']
        selected_drivers = serializer.validated_data['selected_drivers']

        logger.info(f"Creating race: circuit={circuit.name}, date={date}, drivers={len(selected_drivers)}")

        race = Race.objects.create(circuit=circuit, date=date)
        logger.info(f"Race created with ID={race.id}")

        for idx, driver_data in enumerate(selected_drivers, 1):
            driver_name = driver_data.get('name')
            logger.info(f"Processing driver {idx}/{len(selected_drivers)}: {driver_name}")

            driver, created = Driver.objects.get_or_create(name=driver_name)
            if created:
                logger.info(f"  Created new driver: {driver_name}")
            else:
                logger.info(f"  Using existing driver: {driver_name}")

            # Parse lap times and calculate statistics
            from datetime import timedelta
            laps_data = driver_data.get('laps', [])
            logger.info(f"  Processing {len(laps_data)} laps")

            # Debug: Log first lap structure
            if laps_data:
                logger.info(f"  First lap structure: {laps_data[0]}")

            # Collect all lap durations
            lap_durations = []
            total_time = timedelta(0)

            for lap in laps_data:
                # Handle both 'lap_time' and 'time' keys for backwards compatibility
                lap_time_str = lap.get('lap_time') or lap.get('time')
                if not lap_time_str:
                    logger.warning(f"  Lap missing time field: {lap}")
                    continue

                lap_duration = parse_time_to_duration(lap_time_str)
                if lap_duration:
                    lap_durations.append(lap_duration)
                    total_time += lap_duration

            # Calculate fastest and average lap from actual lap times (NOT from OCR)
            fastest_lap = min(lap_durations) if lap_durations else None
            average_lap = total_time / len(lap_durations) if lap_durations else None

            logger.info(f"  Total laps: {len(lap_durations)}")
            logger.info(f"  Total time: {format_duration(total_time) if total_time.total_seconds() > 0 else 'N/A'}")
            logger.info(f"  Fastest lap (calculated): {format_duration(fastest_lap)}")
            logger.info(f"  Average lap (calculated): {format_duration(average_lap)}")

            # Create race result with calculated values
            race_result = RaceResult.objects.create(
                race=race,
                driver=driver,
                total_time=total_time if total_time.total_seconds() > 0 else None,
                fastest_lap=fastest_lap,
                average_lap=average_lap
            )
            logger.info(f"  Race result created with ID={race_result.id}")

            # Save individual lap times
            lap_count = 0
            for lap_data in laps_data:
                # Handle both 'lap_time' and 'time' keys for backwards compatibility
                lap_time_str = lap_data.get('lap_time') or lap_data.get('time')
                if not lap_time_str:
                    logger.warning(f"  Skipping lap without time: {lap_data}")
                    continue

                lap_time = parse_time_to_duration(lap_time_str)
                if lap_time:
                    LapTime.objects.create(
                        race_result=race_result,
                        lap_number=lap_data.get('lap_number', lap_count + 1),
                        lap_time=lap_time
                    )
                    lap_count += 1

            logger.info(f"  Saved {lap_count} lap times")

        logger.info(f"=== Save Race Results Completed Successfully: Race ID={race.id} ===")

        return Response(
            RaceDetailSerializer(race).data,
            status=status.HTTP_201_CREATED
        )


class LeaderboardView(APIView):
    """Get leaderboard with best average and fastest lap (overall and last year). Optional filter by circuit."""

    def get(self, request):
        # Optional circuit filter
        circuit_id = request.query_params.get('circuit')

        drivers = Driver.objects.all()

        # Overall rankings
        best_avg_overall = []
        fastest_lap_overall = []

        # Last year rankings
        one_year_ago = datetime.now().date() - timedelta(days=365)
        best_avg_last_year = []
        fastest_lap_last_year = []

        for driver in drivers:
            all_results = RaceResult.objects.filter(driver=driver)

            # Apply circuit filter if provided
            if circuit_id:
                try:
                    circuit_id_int = int(circuit_id)
                    all_results = all_results.filter(race__circuit_id=circuit_id_int)
                except ValueError:
                    pass

            if all_results.exists():
                # Overall stats
                avg_overall = all_results.aggregate(Avg('average_lap'))['average_lap__avg']
                fastest_overall = all_results.aggregate(Min('fastest_lap'))['fastest_lap__min']

                if avg_overall:
                    best_avg_overall.append({
                        "driver_id": driver.id,
                        "driver_name": driver.name,
                        "average_lap": format_duration(avg_overall)
                    })

                if fastest_overall:
                    fastest_lap_overall.append({
                        "driver_id": driver.id,
                        "driver_name": driver.name,
                        "fastest_lap": format_duration(fastest_overall)
                    })

                # Last year stats
                last_year_results = all_results.filter(race__date__gte=one_year_ago)

                if last_year_results.exists():
                    avg_last_year = last_year_results.aggregate(Avg('average_lap'))['average_lap__avg']
                    fastest_last_year = last_year_results.aggregate(Min('fastest_lap'))['fastest_lap__min']

                    if avg_last_year:
                        best_avg_last_year.append({
                            "driver_id": driver.id,
                            "driver_name": driver.name,
                            "average_lap": format_duration(avg_last_year)
                        })

                    if fastest_last_year:
                        fastest_lap_last_year.append({
                            "driver_id": driver.id,
                            "driver_name": driver.name,
                            "fastest_lap": format_duration(fastest_last_year)
                        })

        # Sort by time (lower is better)
        best_avg_overall.sort(key=lambda x: x['average_lap'] if x['average_lap'] else 'Z')
        fastest_lap_overall.sort(key=lambda x: x['fastest_lap'] if x['fastest_lap'] else 'Z')
        best_avg_last_year.sort(key=lambda x: x['average_lap'] if x['average_lap'] else 'Z')
        fastest_lap_last_year.sort(key=lambda x: x['fastest_lap'] if x['fastest_lap'] else 'Z')

        return Response({
            "overall": {
                "best_average_lap": best_avg_overall,
                "fastest_lap": fastest_lap_overall
            },
            "last_year": {
                "best_average_lap": best_avg_last_year,
                "fastest_lap": fastest_lap_last_year
            }
        }, status=status.HTTP_200_OK)
