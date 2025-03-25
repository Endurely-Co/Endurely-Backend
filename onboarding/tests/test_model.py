import pytest
from django.core.exceptions import ValidationError
from onboarding.models import OTP


@pytest.mark.django_db
def test_valid_user(otp):
    assert otp.user.id > 0


@pytest.mark.django_db
def test_valid_otp(otp, user):
    otp.user = user
    assert otp.user is not None


@pytest.mark.django_db
def test_otp_char_count(otp) -> None:
    otp.otp = '1237614632'

    with pytest.raises(ValidationError) as e:
        otp.full_clean()

    assert 'Ensure this value has at most 6 characters' in str(e.value)
