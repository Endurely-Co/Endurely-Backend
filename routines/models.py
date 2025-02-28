from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models import CharField, DurationField, IntegerField, BooleanField
from django.utils.timezone import now

from utils.fitmodels import FitModel


class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ('UB', 'Upper Body'),
        ('LB', 'Lower Body'),
        ('CO', 'Core & Abs'),
        ('EX', 'Explosive & Athletic Training'),
        ('CM', 'Conditioning & Mobility'),
    ]

    key = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=50)  # name of an excercise
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.key})"


class FitnessRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, default=1, on_delete=models.CASCADE)
    routine_name = CharField(max_length=50, null=False)
    routine_set = IntegerField(default=0, null=False)
    routine_reps = IntegerField(default=0, null=False)
    routine_duration = DurationField(null=False, default=timedelta)
    completed = BooleanField(default=False, null=False)
    created_at = models.DateTimeField(default=now, null=False)


class Nutrition(models.Model):
    NUTRIENT_CHOICES = [
        ("CAL", "Calories"),
        ("PRO", "Protein"),
        ("CARB", "Carbohydrates"),
        ("FAT", "Total Fat"),
        ("SFAT", "Saturated Fat"),
        ("TFAT", "Trans Fat"),
        ("CHOL", "Cholesterol"),
        ("SOD", "Sodium"),
        ("POT", "Potassium"),
        ("FIB", "Dietary Fiber"),
        ("SUG", "Sugars"),
        ("VITA", "Vitamin A"),
        ("VITC", "Vitamin C"),
        ("VITD", "Vitamin D"),
        ("VITE", "Vitamin E"),
        ("VITK", "Vitamin K"),
        ("VITB1", "Thiamine (Vitamin B1)"),
        ("VITB2", "Riboflavin (Vitamin B2)"),
        ("VITB3", "Niacin (Vitamin B3)"),
        ("VITB5", "Pantothenic Acid (Vitamin B5)"),
        ("VITB6", "Vitamin B6"),
        ("VITB7", "Biotin (Vitamin B7)"),
        ("VITB9", "Folate (Vitamin B9)"),
        ("VITB12", "Vitamin B12"),
        ("CALC", "Calcium"),
        ("IRON", "Iron"),
        ("MAG", "Magnesium"),
        ("PHOS", "Phosphorus"),
        ("ZINC", "Zinc"),
        ("COPP", "Copper"),
        ("MANG", "Manganese"),
        ("SELE", "Selenium"),
        ("IOD", "Iodine"),
        ("CHRO", "Chromium"),
        ("MOLY", "Molybdenum"),
        ("OMEGA3", "Omega-3 Fatty Acids"),
        ("OMEGA6", "Omega-6 Fatty Acids"),
        ("WATER", "Water"),
    ]

    created_at = models.DateTimeField(default=now, null=False)
    nutrient = models.CharField(max_length=50, default=NUTRIENT_CHOICES[0], choices=NUTRIENT_CHOICES)
    food_name = models.CharField(max_length=100, null=False, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class MealRecommendation(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_meal = models.CharField(max_length=100)


class FitnessRecommendation(models.Model):
    SEX = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('P', 'Prefer not to say')
    ]
    created_at = models.DateTimeField(default=now, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    height = models.FloatField(null=False, default=0)
    sex = models.CharField(default=SEX[-1], choices=SEX, max_length=20)
    fitness_goal = models.CharField(null=False, default='')