from django.test import TestCase
from django.test import SimpleTestCase
from django.test.utils import isolate_apps

from django.db import models


# Create your tests here.

class TestModelDefinition(SimpleTestCase):
    @isolate_apps("app_label")
    def test_model_definition(self):
        class TestModel(models.Model):
            pass


class OnboardTestCase(TestCase):

    def setUp(self):
        pass
