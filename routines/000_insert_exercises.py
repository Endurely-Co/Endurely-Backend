from django.db import migrations, models


def create_exercises(apps, schema_editor):
    Exercise = apps.get_model('your_app_name', 'Exercise')  # Replace 'your_app_name' with your actual app name
    exercises = [
        ("PUSH01", "Push-Up",
         "1. Start in a high plank position with hands under shoulders.\n2. Lower your body until your chest nearly touches the floor.\n3. Push back up to the starting position.",
         "UB"),
        ("BENCH01", "Bench Press",
         "1. Lie on a bench with feet flat on the floor.\n2. Grip the bar slightly wider than shoulder-width.\n3. Lower the bar to your chest, then press it back up.",
         "UB"),
        ("DIPS01", "Dips",
         "1. Grip parallel bars and lift yourself up.\n2. Lower your body by bending your elbows.\n3. Push yourself back up to the starting position.",
         "UB"),
        ("PULL01", "Pull-Up",
         "1. Grip a pull-up bar with palms facing away.\n2. Pull yourself up until your chin is above the bar.\n3. Lower yourself back down in a controlled manner.",
         "UB"),
        ("ROW01", "Bent-Over Row",
         "1. Hold a barbell with a shoulder-width grip.\n2. Bend at your hips while keeping a straight back.\n3. Pull the bar towards your torso, then lower it back.",
         "UB"),
        ("SHOULDER01", "Overhead Press",
         "1. Hold a barbell or dumbbells at shoulder height.\n2. Press the weight overhead until arms are fully extended.\n3. Lower back to the starting position.",
         "UB"),
        ("CURL01", "Bicep Curl",
         "1. Hold a dumbbell in each hand with palms facing forward.\n2. Curl the weights towards your shoulders.\n3. Lower them back down slowly.",
         "UB"),
        ("TRICEP01", "Tricep Extension",
         "1. Hold a dumbbell overhead with both hands.\n2. Lower it behind your head by bending your elbows.\n3. Extend your arms back to the starting position.",
         "UB"),
        ("SQUAT01", "Squat",
         "1. Stand with feet shoulder-width apart.\n2. Lower your hips back and down, keeping your chest up.\n3. Push through your heels to return to standing.",
         "LB"),
        ("DEADLIFT01", "Deadlift",
         "1. Stand with feet hip-width apart and grip the barbell.\n2. Hinge at your hips and lift the bar while keeping your back straight.\n3. Lower the bar back down in a controlled motion.",
         "LB"),
        ("LUNGES01", "Lunges",
         "1. Step forward with one leg and lower your hips.\n2. Keep your front knee aligned with your ankle.\n3. Push back to the starting position and switch legs.",
         "LB"),
        ("LEGPRESS01", "Leg Press",
         "1. Sit on the leg press machine with feet shoulder-width apart.\n2. Press the platform away until legs are extended.\n3. Slowly lower it back down.",
         "LB"),
        ("CALF01", "Calf Raise",
         "1. Stand with feet hip-width apart.\n2. Rise onto your toes as high as possible.\n3. Lower back down slowly.",
         "LB"),
        ("HAMSTRING01", "Hamstring Curl",
         "1. Lie face down on the hamstring curl machine.\n2. Curl your legs towards your glutes.\n3. Lower back down slowly.",
         "LB"),
        ("PLANK01", "Plank",
         "1. Get into a forearm plank position.\n2. Keep your body straight and core engaged.\n3. Hold for the desired duration.",
         "CO"),
        ("CRUNCH01", "Crunch",
         "1. Lie on your back with knees bent.\n2. Lift your upper body towards your knees.\n3. Lower back down slowly.",
         "CO"),
        ("LEGRAISE01", "Leg Raise",
         "1. Lie on your back with legs extended.\n2. Lift your legs up to a 90-degree angle.\n3. Lower them back down without touching the floor.",
         "CO"),
        ("RUSSIANTWIST01", "Russian Twist",
         "1. Sit with knees bent and lean back slightly.\n2. Rotate your torso side to side while holding a weight.",
         "CO"),
        ("BOXJUMP01", "Box Jump",
         "1. Stand in front of a sturdy box.\n2. Jump onto the box, landing softly.\n3. Step back down and repeat.",
         "EX"),
        ("MEDBALLSLAM01", "Medicine Ball Slam",
         "1. Hold a medicine ball overhead.\n2. Slam it down forcefully.\n3. Catch and repeat.", "EX"),
        ("SPRINT01", "Sprint",
         "1. Start in a sprint stance.\n2. Explode forward and run at max effort.\n3. Slow down gradually.", "EX"),
        ("AGILITYLADDER01", "Agility Ladder Drills",
         "1. Perform quick foot movements through a ladder.\n2. Maintain control and speed.\n3. Repeat with different patterns.",
         "EX"),
        ("RUN01", "Running",
         "1. Maintain a steady pace with proper posture.\n2. Control your breathing.\n3. Adjust speed based on endurance goals.",
         "CM"),
        ("JUMPROPE01", "Jump Rope",
         "1. Hold the rope handles and start swinging.\n2. Jump over the rope with each rotation.\n3. Maintain a steady rhythm.",
         "CM"),
        ("BURPEE01", "Burpee",
         "1. Start in a standing position.\n2. Drop into a squat and place hands on the floor.\n3. Jump back into a plank, do a push-up, jump forward, and stand.",
         "CM"),
        ("ROWING01", "Rowing Machine",
         "1. Sit on the rowing machine with feet strapped in.\n2. Pull the handle towards your chest while pushing with legs.\n3. Return to starting position.",
         "CM"),
        ("CYCLING01", "Cycling",
         "1. Adjust the bike seat for comfort.\n2. Pedal at a consistent pace.\n3. Maintain good posture and breathing.",
         "CM"),
        ("YOGA01", "Yoga",
         "1. Move through various poses with control.\n2. Focus on breathing and flexibility.\n3. Hold each pose for a few breaths.",
         "CM"),
    ]

    Exercise.objects.bulk_create([
        Exercise(key=key, name=name, description=steps, category=cat)
        for key, name, steps, cat in exercises
    ])


def reverse_exercises(apps, schema_editor):
    Exercise = apps.get_model('your_app_name', 'Exercise')
    Exercise.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = []  # Add the proper migration dependencies

    operations = [
        migrations.RunPython(create_exercises, reverse_exercises),
    ]
