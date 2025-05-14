from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from utils.api import api_error, api_created_success
from utils.exceptions import InvalidNameException, WeakPasswordError
from utils.validator import validate_email, \
    validate_username, check_password, check_name
from .acct_type import AccountType
from .serializers import CreateUserSerializer


# Create your views here.
class CreateAccountView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if type(request.data) is not dict:
            return api_error("Invalid request type")
        try:
            if validate_email(request.data['email']) \
                    and validate_username(request.data['username']):
                first_name = check_name(request.data['first_name'])
                last_name = check_name(request.data['last_name'])
                user = User.objects.create_user(email=request.data['email'],
                                                password=check_password(request.data['password']),
                                                username=request.data['username'])
                user.first_name = first_name
                user.last_name = last_name
                user.acct_type = AccountType.unverify
                user.save()

                return api_created_success({
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "acct_type": user.acct_type
                })
            else:
                return api_error("Invalid email or username")
        except IntegrityError:
            return api_error("Username already exist. Please try again")
        except KeyError as keyErr:
            return api_error('{} is missing'.format(keyErr.__str__()))
        except (WeakPasswordError, InvalidNameException, TypeError) as error:
            return api_error(error.__str__())


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),  # Refresh token (Used to get a new access token)
        'access': str(refresh.access_token),  # Main token used for authentication
    }


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return api_error("Username and password are required")

        user = authenticate(username=username, password=password)
        if user:
            tokens = get_tokens_for_user(user)  # Generate JWT tokens
            return api_created_success({
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "token": tokens['access'],  # Return access token for authentication
                "refresh_token": tokens['refresh'],  # Refresh token for re-authentication
            })
        return api_error("Invalid username or password")


class Logout(APIView):
    def get(self, request):
        # simply delete the token to force a login
        logout(request)
        return Response(status=status.HTTP_200_OK)

