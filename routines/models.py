from django.db import models
from django.contrib.auth.models import User
from django.db.models import CharField


class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ('UB', 'Upper Body'),
        ('LB', 'Lower Body'),
        ('CO', 'Core & Abs'),
        ('EX', 'Explosive & Athletic Training'),
        ('CM', 'Conditioning & Mobility'),
    ]

    key = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.key})"


class FitnessRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, default=1, on_delete=models.CASCADE)
    routine_name = CharField(max_length=50, null=False)
