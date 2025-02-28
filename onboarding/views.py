from django.db.utils import IntegrityError

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from utils.api import api_error, api_success, check_input
from utils.exceptions import InvalidNameException, WeakPasswordError
from utils.validator import Messages, validate_email, \
    validate_username, check_password, check_name
from django.core import serializers
from django.contrib.auth import authenticate, logout
import json

from django.contrib.auth.models import User
from .models import OTP
from .serializers import CreateUserSerializer, CreateOTPSerializer

from random import randint
import smtplib
from email.mime.multipart import MIMEMultipart  # for easy segregation of email sections
from email.mime.text import MIMEText
from datetime import timedelta
from django.utils import timezone
from .acct_type import AccountType


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

                return api_success({
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
            return api_success({
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


class CreateGetOTPView(generics.CreateAPIView):
    serializer_class = CreateOTPSerializer

    # function which uses the OTP model

    # input should be:
    # - valid username/email

    # output should be (no actual values are necessary to be returned, only for debug purposes):
    # - SUCCESS if the following conditions are met:
    # ----- there exists a user with the inputted username and/or email address
    # ----- the email is succesfully sent
    # - FAIL if any of the above conditions are not met
    def post(self, request, custom_otp: str = None, *args, **kwargs):
        target_user: User | None = None

        # following if/elif/else statements find the user based on the inputted email/username
        if "username" in request.data:
            try:
                target_user = User.objects.get(username=request.data['username'])
            except User.DoesNotExist as notExistErr:
                return api_error(f"Could not find User. {notExistErr.__str__()}")
        elif "email" in request.data:
            try:
                target_user = User.objects.get(email=request.data['email'])
            except User.DoesNotExist as notExistErr:
                return api_error(f"Could not find User. {notExistErr.__str__()}")
        else:
            return api_error("No valid email or username was provided.")

        # generates OTP and send to user, contains 6 digits from 0-9
        otp = (f"{randint(0, 999999):06d}" if custom_otp == None else custom_otp)

        try:
            # REMOVE FROM GITHUB IF POSSIBLE
            SENDER_EMAIL = 'fitfocusup@gmail.com'  # The email you setup to send the email using app password
            SENDER_EMAIL_APP_PASSWORD = 'ywhq vvqt fqri jvbb'  # The app password you generated

            # Construct SMTP server
            smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpserver.ehlo()
            smtpserver.login(SENDER_EMAIL, SENDER_EMAIL_APP_PASSWORD)

            # Create email contents
            # NOTE: for new lines, use <br> as the email formatter is done via HTML.
            message = MIMEMultipart()
            message["To"] = target_user.email
            message["From"] = SENDER_EMAIL
            message["Subject"] = "Your FitFocus One-Time Password"
            messageText = MIMEText(
                f"Your FitFocus OTP is {otp}.<br>This OTP will expire within 5 minutes.<br>Should you require a new OTP, request another one.",
                "html")
            message.attach(messageText)

            notes_text = "Email successfully sent. Don\'t see it? Be sure to check spam folders."

            # Send the email and close the server
            smtpserver.sendmail(
                from_addr=SENDER_EMAIL,
                to_addrs=target_user.email,
                msg=message.as_string()
            )
            smtpserver.close()

            # create/update the existing OTP in the OTP table
            # created_at and expiry_time SHOULD automatically update
            # new_otp does not set itself exactly equal to 5 mins past created at,
            # so it must be manually set after creating the object

            new_otp: OTP | None = None
            try:
                new_otp = OTP.objects.get(
                    user=target_user
                )
            except OTP.DoesNotExist:
                new_otp = OTP.objects.create(
                    user=target_user
                )

            new_otp.otp = otp
            new_otp.created_at = timezone.now()
            new_otp.expiry_time = new_otp.created_at + timezone.timedelta(minutes=5)

            # MAKE SURE TO SAVE WHEN UPDATING. 15 minutes of bugfixing to find out objects dont save without this lol
            new_otp.save()

            # returns all the data from the OTP.
            # "user" displays the username as User objects will not be displayed in a JSON format for security reasons, 
            return api_success({
                "user": new_otp.user.username,
                "otp": new_otp.otp,
                "created_at": new_otp.created_at,
                "expiry_time": new_otp.expiry_time,
            })
        except smtplib.SMTPException as smtpErr:
            return api_error(f"Email failed to send: {smtpErr.__str__()}")


class ValidateOTPView(generics.CreateAPIView):
    serializer_class = CreateOTPSerializer

    # post should include:
    # - username/email to the account
    # - attempted OTP (6 digits from 0-9)

    # api call should return a single response:
    # - "success" if all of the conditions are met:
    # ----- there is a user with the correct username and/or email address
    # ----- attempt datetime <= OTP expiry_time
    # ----- attempted OTP = stored OTP
    # - "fail" OR an error description if any of the above conditions are not met
    def post(self, request, *args, **kwargs):
        target_user: User | None = None

        # following if/elif/else statements find the user based on the inputted email/username
        if "email" in request.data:
            try:
                target_user = User.objects.get(email=request.data["email"])
            except User.DoesNotExist as notExistErr:
                return api_error(f"Could not find User. {notExistErr.__str__()}")
        elif "username" in request.data:
            try:
                target_user = User.objects.get(username=request.data["username"])
            except User.DoesNotExist as notExistErr:
                return api_error(f"Could not find User. {notExistErr.__str__()}")
        else:
            return api_error("No valid email or username was provided.")

        # determines if an OTP was included
        if "otp" not in request.data:
            return api_error("No OTP was provided.")

        # gathers the OTP data for the user
        stored_otp = OTP.objects.get(user=target_user)

        # checks if the OTP has passed expiry
        if timezone.now() > stored_otp.expiry_time:
            return api_error(f"The OTP has expired. Request a new OTP.")

        if request.data["otp"].strip() == stored_otp.otp:
            return api_success("success")
        else:
            return api_error("The OTP is incorrect.")
