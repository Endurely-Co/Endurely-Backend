from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


# Create your models here.
class Fitness(models.Model):
    name = models.CharField(default='', max_length=50)
    description = models.CharField(default='', max_length=1000)


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
    recommendation = models.ForeignKey(Fitness, on_delete=models.CASCADE, default=0)
