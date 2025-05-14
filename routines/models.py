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

    key = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)  # name of an excercise
    description = models.CharField(max_length=1000, null=False, default='')
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.key})"


class UserExercise(models.Model):
    duration = DurationField(null=False, default=timedelta)
    created_at = models.DateTimeField(default=now, null=False)
    image = CharField(max_length=300, null=True)
    completed = BooleanField(default=False, null=False)
    exercise = models.ForeignKey(Exercise, default=1, on_delete=models.CASCADE)


class FitnessRoutine(models.Model):

    WEEK_DAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(UserExercise, default=1, on_delete=models.CASCADE)
    routine_name = CharField(max_length=50, null=False)
    routine_id = CharField(default='', null=False, max_length=40)
    completed = BooleanField(default=False, null=False)
    created_at = models.DateTimeField(default=now, null=False)
    start_date = models.DateTimeField(null=False, default=now)
