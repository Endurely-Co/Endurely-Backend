from django.db import models
from django.utils.timezone import now

from meal.models import MealPlan


class FitModel(models.Model):
    created_at = models.DateTimeField(default=now, null=False)


def update_or_create_meal_plan(meal_plan_id, user, meal_date_time, food_item=None):
    defaults = {
        "user": user,
    }
    if food_item:
        defaults["food_item"] = food_item
        defaults["food_name"] = food_item.item
        defaults['meal_date_time'] = meal_date_time
    meal_plan, created = MealPlan.objects.update_or_create(
        meal_plan_id=meal_plan_id,  # Lookup field
        defaults=defaults
    )
    return meal_plan, created


def update_or_create_meal_plan_date(meal_plan_id, user, meal_date_time, food_item=None):
    defaults = {
        "user": user,
    }
    if food_item:
        defaults["food_item"] = food_item
        defaults["food_name"] = food_item.item
        #defaults['meal_plan_id'] = meal_plan_id
    meal_plan, created = MealPlan.objects.update_or_create(
        meal_date_time=meal_date_time,  # Lookup field
        meal_plan_id=meal_plan_id,
        defaults=defaults
    )
    return meal_plan, created


"""
MealPlan.objects.update_or_create(
                    user=user,
                    meal_plan_id=plan_id,
                    food_name=plan['meal'],
                    food_item=food_item,
                    meal_date_time=request.data['meal_date_time']
                )
"""
