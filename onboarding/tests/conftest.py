import pytest
from datetime import date
from django.contrib.auth import get_user_model

from onboarding.models import OTP

User = get_user_model()

# {'username': 'existing_username', 'password': 'valid_password'}


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="testuser1", password="abC@124")
