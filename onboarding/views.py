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


class CreateAccountView(generics.CreateAPIView):
    """
    API view to create a new user account.

    This view handles user registration, including validation of input data
    and creation of a new user in the database.
    """
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to create a new user account.

        Args:
            request (Request): The request object containing user data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A JSON response indicating success or failure.
        """
        if type(request.data) is not dict:
            return api_error("Invalid request type")
        try:
            # Validate email and username formats
            if validate_email(request.data['email']) \
                    and validate_username(request.data['username']):
                # Validate first and last names
                first_name = check_name(request.data['first_name'])
                last_name = check_name(request.data['last_name'])

                # Create a new user using validated data
                user = User.objects.create_user(email=request.data['email'],
                                                password=check_password(request.data['password']),
                                                username=request.data['username'])

                # Set additional user attributes
                user.first_name = first_name
                user.last_name = last_name
                user.acct_type = AccountType.unverify  # Set default account type
                user.save()

                # Return a success response with user details
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
            # Handle username already exists
            return api_error("Username already exist. Please try again")
        except KeyError as keyErr:
            # Handle missing required fields
            return api_error('{} is missing'.format(keyErr.__str__()))
        except (WeakPasswordError, InvalidNameException, TypeError) as error:
            # Handle validation errors
            return api_error(error.__str__())


def get_tokens_for_user(user):
    """
    Generates JWT tokens (refresh and access) for a given user.

    Args:
        user (User): The user object for whom to generate tokens.

    Returns:
        dict: A dictionary containing the refresh and access tokens.
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),  # Refresh token (Used to get a new access token)
        'access': str(refresh.access_token),  # Main token used for authentication
    }


class LoginView(APIView):
    """
    API view to handle user login and token generation.

    Authenticates the user based on username and password and returns JWT tokens
    upon successful authentication.
    """

    def post(self, request):
        """
        Handles the POST request for user login.

        Args:
            request (Request): The request object containing username and password.

        Returns:
            Response: A JSON response containing user details and tokens upon successful login,
                      or an error message upon failure.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if username and password are provided
        if not username or not password:
            return api_error("Username and password are required")

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user:
            # Generate JWT tokens for the authenticated user
            tokens = get_tokens_for_user(user)
            return api_created_success({
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "token": tokens['access'],  # Return access token for authentication
                "refresh_token": tokens['refresh'],  # Refresh token for re-authentication
            })
        # Return an error if authentication fails
        return api_error("Invalid username or password")


class Logout(APIView):
    """
    API view to handle user logout.

    Invalidates the user's session by calling the `logout` function.
    """

    def get(self, request):
        """
        Handles the GET request for user logout.

        Args:
            request (Request): The request object.

        Returns:
            Response: A 200 OK response indicating successful logout.
        """
        # simply delete the token to force a login
        logout(request)
        return Response(status=status.HTTP_200_OK)
