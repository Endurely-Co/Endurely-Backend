from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Create your models here.

class MealPlan(models.Model):
    meal = models.CharField(default='', null=False, max_length=70)
    calorie = models.FloatField(default=0, null=False)
    nutrition = models.CharField(max_length=1000, null=False, default='')
    created_at = models.DateTimeField(default=now, null=False)


class MealRecommendation(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_meal = models.CharField(max_length=100)
