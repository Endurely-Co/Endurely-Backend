from django.db import migrations, models


def create_exercises(apps, schema_editor):
    Exercise = apps.get_model('routines', 'Exercise')  # Replace 'routines' with your actual app name
    exercises = [
        ("PUSH01", "Push-Up", "A bodyweight exercise targeting the chest, shoulders, and triceps.", "UB"),
        ("BENCH01", "Bench Press", "A weightlifting exercise for chest, shoulders, and triceps.", "UB"),
        ("DIPS01", "Dips", "A compound movement for triceps, chest, and shoulders.", "UB"),
        ("PULL01", "Pull-Up", "A bodyweight exercise focusing on back and biceps.", "UB"),
        ("ROW01", "Bent-Over Row", "Strengthens the upper and mid-back using a barbell or dumbbells.", "UB"),
        ("SHOULDER01", "Overhead Press", "Builds shoulder strength using a barbell or dumbbells.", "UB"),
        ("CURL01", "Bicep Curl", "Isolates the biceps using dumbbells, barbells, or cables.", "UB"),
        ("TRICEP01", "Tricep Extension", "Works the triceps using dumbbells, cables, or a barbell.", "UB"),
        ("SQUAT01", "Squat", "A full-leg exercise targeting quads, hamstrings, and glutes.", "LB"),
        ("DEADLIFT01", "Deadlift", "A compound movement engaging legs, back, and core.", "LB"),
        ("LUNGES01", "Lunges", "Unilateral leg movement for quads, glutes, and balance.", "LB"),
        ("LEGPRESS01", "Leg Press", "A machine-based exercise targeting leg muscles.", "LB"),
        ("CALF01", "Calf Raise", "Strengthens the calf muscles.", "LB"),
        ("HAMSTRING01", "Hamstring Curl", "Isolates and strengthens the hamstrings.", "LB"),
        ("PLANK01", "Plank", "A core stability exercise that strengthens the entire midsection.", "CO"),
        ("CRUNCH01", "Crunch", "A classic ab exercise to target the upper abdominal muscles.", "CO"),
        ("LEGRAISE01", "Leg Raise", "Engages the lower abs and hip flexors.", "CO"),
        ("RUSSIANTWIST01", "Russian Twist", "Improves oblique strength and rotational core stability.", "CO"),
        ("BOXJUMP01", "Box Jump", "Develops power and explosiveness in the legs.", "EX"),
        ("MEDBALLSLAM01", "Medicine Ball Slam", "A full-body power exercise for strength and endurance.", "EX"),
        ("SPRINT01", "Sprint", "A high-intensity running exercise that enhances speed and conditioning.", "EX"),
        ("AGILITYLADDER01", "Agility Ladder Drills", "Improves foot speed, coordination, and agility.", "EX"),
        ("RUN01", "Running", "A cardiovascular workout that improves endurance.", "CM"),
        ("JUMPROPE01", "Jump Rope", "Great for cardio, agility, and lower-body endurance.", "CM"),
        ("BURPEE01", "Burpee", "A full-body conditioning exercise combining strength and cardio.", "CM"),
        ("ROWING01", "Rowing Machine", "Works the back, arms, and cardiovascular system.", "CM"),
        ("CYCLING01", "Cycling", "A cardio exercise focusing on endurance and leg strength.", "CM"),
        ("YOGA01", "Yoga", "Improves flexibility, balance, and overall mobility.", "CM"),
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
