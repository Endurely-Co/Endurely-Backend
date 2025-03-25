import pytest
from datetime import date, datetime

from _datetime import UTC
from django.contrib.auth import get_user_model
from django.utils import timezone

from onboarding.models import OTP

User = get_user_model()


# {'username': 'existing_username', 'password': 'valid_password'}


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="testuser1", password="abC@124")


@pytest.fixture
def otp(user) -> OTP:
    return OTP.objects.create(
        user=user,
        otp='123453',
        created_at=datetime(2023, 11, 10, 11, 2, 8, 127325, tzinfo=UTC),
        expiry_time=datetime(2025, 11, 20, 20, 8, 7, 127325, tzinfo=UTC)
    )
