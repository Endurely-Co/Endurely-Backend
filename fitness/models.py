from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

# Create your models here.
from django.db import models


class FitnessPlan(models.Model):
    disclaimer = models.TextField()

    def __str__(self):
        return f"Fitness Plan: {self.id}"


class Recommendation(models.Model):
    exercise = models.CharField(max_length=255)
    description = models.TextField()
    frequency = models.CharField(max_length=255)
    justification = models.TextField()

    def __str__(self):
        return f"Recommendation: {self.exercise}"


class UserFitness(models.Model):
    SEX = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('P', 'Prefer not to say')
    ]
    FITNESS_GOALS = [
        ("WEI", "Weight Loss"),
        ("MUS", "Muscle Gain (Hypertrophy)"),
        ("INC", "Increase Strength"),
        ("IMP", "Improve Endurance"),
        ("FLE", "Flexibility and Mobility"),
        ("CAR", "Improve Cardiovascular Health"),
        ("FAT", "Fat Loss and Lean Muscle Tone"),
        ("BOD", "Bodybuilding"),
        ("SPO", "Sports Performance"),
        ("POS", "Post-Surgery Rehab and Recovery"),
        ("IMP", "Improve Posture"),
        ("SPE", "Increase Speed and Agility"),
        ("FUN", "Functional Fitness (everyday movement and strength)"),
        ("MEN", "Improve Mental Health (e.g., reduce stress, anxiety)"),
        ("MAI", "Maintain a Healthy Lifestyle"),
        ("IMB", "Improved Balance and Coordination"),
        ("COR", "Increase Core Strength"),
        ("STA", "Improve Stamina"),
        ("HEA", "Health Maintenance (keep body in good shape)"),
        ("TRA", "Training for a Specific Event (e.g., marathon, triathlon, etc.)")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    height = models.FloatField(null=False, default=0)
    sex = models.CharField(default=SEX[-1], choices=SEX, max_length=20)
    fitness_goal = models.CharField(null=False, default=FITNESS_GOALS[0][0], max_length=80, choices=FITNESS_GOALS)


class FitnessRecommendation(models.Model):
    disclaimer = models.CharField(max_length=255, default='', null=False)
    created_at = models.DateTimeField(default=now, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_fitness = models.ForeignKey(UserFitness, on_delete=models.CASCADE, default=0)
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, default=0)

