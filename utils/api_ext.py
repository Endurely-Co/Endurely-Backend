from rest_framework import permissions
from rest_framework.views import APIView


class AuthenticatedAPIView(APIView):
    # Bearer token is not required in this project which is why this is AllowAny
    # Used to turn on/off authentication.
    permission_classes = [permissions.AllowAny]
