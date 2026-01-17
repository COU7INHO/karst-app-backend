"""
Debug middleware to log all incoming requests.
"""
import logging

logger = logging.getLogger(__name__)


class DebugRequestMiddleware:
    """Log all incoming HTTP requests for debugging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.info("=" * 80)
        logger.info(f"METHOD: {request.method}")
        logger.info(f"PATH: {request.path}")
        logger.info(f"HEADERS: {dict(request.headers)}")

        if request.method == 'POST':
            logger.info(f"POST DATA: {request.POST}")
            if hasattr(request, 'body'):
                try:
                    logger.info(f"BODY: {request.body[:500]}")  # First 500 chars
                except Exception as e:
                    logger.info(f"Could not read body: {e}")

        response = self.get_response(request)

        logger.info(f"RESPONSE STATUS: {response.status_code}")
        logger.info("=" * 80)

        return response
