from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CreateOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'