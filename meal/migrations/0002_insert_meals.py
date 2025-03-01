from django.db import migrations

from meal.models import MealInfo

meal_data = [
    {"meal": "Oatmeal with Berries", "calorie": 250},
    {"meal": "Scrambled Eggs with Spinach", "calorie": 300},
    {"meal": "Grilled Chicken Salad", "calorie": 400},
    {"meal": "Lentil Soup", "calorie": 280},
    {"meal": "Salmon with Roasted Vegetables", "calorie": 450},
    {"meal": "Turkey and Avocado Sandwich", "calorie": 350},
    {"meal": "Greek Yogurt with Granola", "calorie": 200},
    {"meal": "Vegetable Stir-fry with Tofu", "calorie": 380},
    {"meal": "Chicken Breast with Sweet Potato", "calorie": 420},
    {"meal": "Apple and Almond Butter", "calorie": 180},
    {"meal": "Protein Smoothie (Whey, Banana, Almond Milk)", "calorie": 320},
    {"meal": "Tuna Salad (Light Mayo) on Whole Wheat", "calorie": 330},
    {"meal": "Chickpea Curry", "calorie": 410},
    {"meal": "Shrimp and Asparagus", "calorie": 360},
    {"meal": "Whole Wheat Pancakes with Fruit", "calorie": 290},
    {"meal": "Lean Ground Beef with Brown Rice", "calorie": 430},
    {"meal": "Cottage Cheese with Pineapple", "calorie": 220},
    {"meal": "Vegetable Omelette", "calorie": 310},
    {"meal": "Chicken and Vegetable Skewers", "calorie": 390},
    {"meal": "Quinoa Salad with Black Beans and Corn", "calorie": 370},
]


def insert_meal_data(apps, schema_editor):
    meal_plan = apps.get_model('meal', 'MealInfo')  # Replace 'your_app_name'
    meals = [MealInfo(meal=item['meal'], calorie=item['calorie']) for item in meal_data]
    meal_plan.objects.bulk_create(meals)


def remove_meal_data(apps, schema_editor):
    meal_plan = apps.get_model('meal', 'MealInfo')  # Replace 'your_app_name'
    meal_names = [item['meal'] for item in meal_data]
    meal_plan.objects.filter(meal__in=meal_names).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('meal', '0001_initial'),  # Replace with your previous migration
    ]

    operations = [
        migrations.RunPython(insert_meal_data, remove_meal_data),
    ]
