# Generated by Django 4.2.19 on 2025-02-18 15:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0006_alter_otp_expiry_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otp',
            name='expiry_time',
            field=models.DateTimeField(db_comment='When the OTP can no longer be accepted. Default is 5 minutes after when it was created.', default=datetime.datetime(2025, 2, 18, 15, 22, 49, 749913, tzinfo=datetime.timezone.utc)),
        ),
    ]
