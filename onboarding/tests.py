from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from django.test import SimpleTestCase
from django.test.utils import isolate_apps

from django.db import models


# Create your tests here.

class TestModelDefinition(SimpleTestCase):
    @isolate_apps("onboarding")
    def test_model_definition(self):
        class OTP(models.Model):
            pass

        class User(AbstractUser):
            pass


class OnboardTestCase(TestCase):

    def setUp(self):
        pass
