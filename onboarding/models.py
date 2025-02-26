from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default="", null=False, db_comment="The OTP sent to the user.")
    created_at = models.DateTimeField(auto_now=True,
                                      db_comment="When the OTP was created. Useful for restricting the frequency of new OTP generation.")
    expiry_time = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=5),
                                       db_comment="When the OTP can no longer be accepted. Default is 5 minutes after when it was created.")
