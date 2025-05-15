from django.db import models
from django.utils.timezone import now

from meal.models import MealPlan


class FitModel(models.Model):
    """
    An abstract base model that provides a timestamp for creation.

    Attributes:
        created_at (DateTimeField): A timestamp indicating when the object was created.
                                       Defaults to the current time and is non-nullable.
    """
    created_at = models.DateTimeField(default=now, null=False)

    class Meta:
        abstract = True


def update_or_create_meal_plan(meal_plan_id: str, user, meal_date_time, food_item=None):
    """
    Updates an existing MealPlan instance or creates a new one.

    The lookup is based on the meal_plan_id and user. If a matching MealPlan exists,
    its fields are updated with the provided defaults. Otherwise, a new MealPlan
    instance is created with the given meal_plan_id, user, and defaults.

    Args:
        meal_plan_id (str): The unique identifier for the meal plan.
        user: The user associated with the meal plan.
        meal_date_time: The date and time of the meal.
        food_item: An optional FoodItem instance to associate with the meal plan.
                   Defaults to None.

    Returns:
        tuple: A tuple containing the MealPlan instance (the updated or created one)
               and a boolean value indicating if a new meal plan was created (True) or
               an existing one was updated (False).
    """
    defaults = {
        "user": user,
    }
    print("meal_plan_id exists?", meal_plan_id,  MealPlan.objects.filter(meal_plan_id=meal_plan_id, user=user).exists())

    print('food_item----->', food_item.item, food_item)
    if food_item:
        defaults["food_item"] = food_item
        defaults["food_name"] = food_item.item
        defaults['meal_date_time'] = meal_date_time
        defaults['meal_plan_id'] = meal_plan_id
    meal_plan, created = MealPlan.objects.update_or_create(
        meal_plan_id=meal_plan_id,
        user=user,# Lookup field
        defaults=defaults
    )
    return meal_plan, created


def update_or_create_meal_plan_date(meal_plan_id: str, user, meal_date_time, food_item=None):
    """
    Updates an existing MealPlan instance or creates a new one based on meal date and plan ID.

    The lookup is based on the meal_date_time and meal_plan_id. If a matching MealPlan
    exists, its fields are updated with the provided defaults. Otherwise, a new MealPlan
    instance is created with the given meal_date_time, meal_plan_id, and defaults.

    Args:
        meal_plan_id (str): The unique identifier for the meal plan.
        user: The user associated with the meal plan.
        meal_date_time: The specific date and time of the meal to look up or create.
        food_item: An optional FoodItem instance to associate with the meal plan.
                   Defaults to None.

    Returns:
        tuple: A tuple containing the MealPlan instance (the updated or created one)
               and a boolean value indicating if a new meal plan was created (True) or
               an existing one was updated (False).
    """
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