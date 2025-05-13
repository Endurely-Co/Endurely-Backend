from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Create your models here.


class MealInfo(models.Model):
    meal = models.CharField(default='', null=False, max_length=70)
    calorie = models.FloatField(default=0, null=False)
    created_at = models.DateTimeField(default=now, null=False)


class NutritionInfo(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    nutrient = models.CharField(max_length=1000, default='', null=False)
    food_name = models.CharField(max_length=100, null=False, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class FoodItem(models.Model):
    item = models.CharField(max_length=255, default="")
    valid = models.BooleanField()
    macronutrients = models.JSONField(default=list, blank=True)
    vitamins = models.JSONField(default=list, blank=True)
    minerals = models.JSONField(default=list, blank=True)
    other_nutrients = models.CharField(null=True, blank=True, max_length=850, default="")

    def __str__(self):
        return self.item


class MealPlan(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True)
    food_name = models.CharField(null=True, blank=True, max_length=100, default="")
    meal_plan_id = models.CharField(null=True, blank=True, max_length=50, default="")
    meal_date_time = models.DateTimeField(default=now, null=False)


class MealRecommendation(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    recommended_meal = models.CharField(null=True, blank=True, max_length=150, default="")


class Nutrient(models.Model):
    name = models.CharField(max_length=255, default="")
    summary = models.CharField(max_length=250, default="", null=True)

    def __str__(self):
        return self.name
