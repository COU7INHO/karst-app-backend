"""
Authentication views for login/logout.
"""
import logging
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """Login with username and password."""

    permission_classes = []  # Public endpoint

    def post(self, request):
        logger.info("=== Login attempt ===")
        username = request.data.get('username')
        password = request.data.get('password')

        logger.info(f"Username: {username}")

        if not username or not password:
            logger.warning("Missing username or password")
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)

        if user is not None:
            logger.info(f"Authentication successful for user: {username}")
            login(request, user)
            logger.info(f"User {username} logged in successfully")
            return Response(
                {
                    "message": "Login successful",
                    "username": user.username
                },
                status=status.HTTP_200_OK
            )
        else:
            logger.warning(f"Authentication failed for user: {username}")
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """Logout current user."""

    permission_classes = []  # Public endpoint (but requires session)

    def post(self, request):
        logout(request)
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )


class AuthStatusView(APIView):
    """Check if user is authenticated."""

    permission_classes = []  # Public endpoint

    def get(self, request):
        if request.user.is_authenticated:
            return Response(
                {
                    "authenticated": True,
                    "username": request.user.username
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"authenticated": False},
                status=status.HTTP_200_OK
            )
