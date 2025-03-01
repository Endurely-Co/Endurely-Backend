from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from routines.models import NutritionInfo


# Create your models here.


class MealInfo(models.Model):
    meal = models.CharField(default='', null=False, max_length=70)
    calorie = models.FloatField(default=0, null=False)
    created_at = models.DateTimeField(default=now, null=False)


class MealPlan(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    meal = models.ForeignKey(MealInfo, on_delete=models.CASCADE, default=1)
    nutrient = models.ForeignKey(NutritionInfo, on_delete=models.CASCADE, null=True)


class MealRecommendation(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    recommended_meal = models.CharField(max_length=100)
