from django.db import migrations, models


def create_exercises(apps, schema_editor):
    Exercise = apps.get_model('routines', 'Exercise')  # Replace 'routines' with your actual app name
    exercises = [

    ]

    Exercise.objects.bulk_create([
        Exercise(key=key, name=name, description=desc, category=cat)
        for key, name, desc, cat in exercises
    ])


def reverse_exercises(apps, schema_editor):
    Exercise = apps.get_model('routines', 'Exercise')
    Exercise.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('routines', '0008_alter_exercise_key'),
    ]  # Add the proper migration dependencies

    operations = [
        migrations.RunPython(create_exercises, reverse_exercises),
    ]
