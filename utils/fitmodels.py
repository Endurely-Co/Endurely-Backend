from django.db import models
from django.utils.timezone import now


class FitModel(models.Model):
    created_at = models.DateTimeField(default=now, null=False)
