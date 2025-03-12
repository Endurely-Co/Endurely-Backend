import uuid

from django.contrib.auth.models import User
from django.db import transaction
from django.utils.timezone import now

from meal.models import MealPlan, MealInfo, NutritionInfo, FoodItem
from meal.serializers import MealPlanSerializer, MealInfoSerializer, NutritionSerializer, FoodItemSerializer
from utils.api import api_created_success, api_error, api_success
from utils.api_ext import AuthenticatedAPIView
from utils.fitmodels import update_or_create_meal_plan
from utils.gemini import GeminiApi


# Create your views here.

class MealRecommendationView(AuthenticatedAPIView):

    def get(self, _):
        meal_data = MealInfo.objects.all()
        serializer = MealInfoSerializer(meal_data, many=True)
        return api_created_success(serializer.data)

    def post(self, request, *args, **kwargs):
        serializers = MealInfoSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return api_created_success(serializers.data)
        key_len = len(serializers.errors.keys())
        return api_error('{} {} {}'.format(' and '.join(serializers.errors.keys()),
                                           "are" if key_len > 1 else "is", "missing"))


class MealPlanView(AuthenticatedAPIView):

    def get(self, request, user_id):
        meal_plan_id = request.query_params.get('plan_id')
        meal_plan = MealPlan.objects.filter(user=user_id)
        if meal_plan_id:
            meal_plan = meal_plan.filter(meal_plan_id=meal_plan_id)
        meal_plan_data = MealPlanSerializer(meal_plan, many=True).data
        print("meal_plan", meal_plan)
        for i in range(len(meal_plan)):
            serialized_food = FoodItemSerializer(meal_plan[i].food_item).data
            if meal_plan_id:
                meal_plan_data[i]["nutrients"] = serialized_food
            else:
                meal_plan_data[i]['other_nutrients'] = serialized_food['other_nutrients']
            # print("food_item", )
        return api_success(meal_plan_data)

    def delete(self, request, user_id):
        meal_to_delete = request.query_params.get('plan_id')
        if meal_to_delete:
            meal_plan = MealPlan.objects.filter(user=user_id) \
                .filter(meal_plan_id=meal_to_delete)
            return api_success("Meal plan successfully deleted")
        return api_error("plan_id is required")

    # meal, calorie rm -rf mealplan/migrations
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        meal_plans = request.data.get('meal_plans')
        if not meal_plans:
            return api_error("meal_plans is absent")

        if type(meal_plans) is not list:
            return api_error("meal_plans is not valid. Expected: list of meal plans")

        if len(meal_plans) > 4:
            return api_error("meal_plans too many meal plans")
        plan_id = "".join(sorted([str(mp['food_item_id']) for mp in meal_plans]))
        user = User.objects.get(pk=request.data['user'])
        meal_plan_response, meal_plan_id = [], None
        for plan in meal_plans:
            try:
                food_item = FoodItem.objects.get(pk=plan['food_item_id'])
            except FoodItem.DoesNotExist:
                return api_error("food item doesn't exist")

            meal_plan = MealPlan.objects.filter(meal_plan_id=plan['food_item_id'])
            if not meal_plan.exists():
                meal_plan = update_or_create_meal_plan(plan_id,
                                                       user, request.data['meal_date_time'], food_item)

        return api_created_success({"message": "Meal plan added successfully"})


class NutrientView(AuthenticatedAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = GeminiApi()

    def get(self, request, user_id):
        meal_plan = MealPlan.objects.filter(user=user_id)
        meal_plan_data = MealPlanSerializer(meal_plan, many=True).data
        for i in range(len(meal_plan)):
            serialized_food = FoodItemSerializer(meal_plan[i].food_item).data
            meal_plan_data[i]['other_nutrients'] = serialized_food['other_nutrients']
            # meal_plan_data[i]["nutrients"] = serialized_food
            # print("food_item", )
        return api_success(meal_plan_data)

    @transaction.atomic
    def post(self, request):
        if not request.data.get('meal') or not request.data.get('user'):
            return api_error("user and meal are required")

        foods = request.data.get('meal').lower().strip()

        # Validate input size
        if not foods or len(foods) <= 2:
            return api_error("Food/drink is invalid. Try again!")

        food_items = [item for item in foods.split(',')]

        if len(food_items) > 2:
            return api_error("Maximum of two food/drink is allowed!")

        # Get user

        try:
            user = User.objects.get(pk=request.data.get('user'))
            response_obj = {
                "user": user.id
            }
        except User.DoesNotExist:
            return api_error("User does not exist")

        # Look in the db
        food_item_query = FoodItem.objects.filter(item=food_items[0]) if len(food_items) < 2 \
            else FoodItem.objects.filter(item__in=[food_items[0], food_items[1]])
        food_exist = food_item_query.exists()
        if food_exist:
            # Both provided foods exists in our db, so no ai call
            if len(food_item_query) >= len(food_items):
                response_obj["nutrients"] = FoodItemSerializer(food_item_query, many=True).data
                return api_created_success(response_obj)
            else:  # absent_q_food
                # Only one food exist in the db
                for food in food_items:
                    if food not in [f.item for f in food_item_query]:
                        foods = food
                print('one exist', food_exist)

        # Get results from gemini API
        gemini_results = self.gemini.nutrients_from_food(foods)['results']

        # Prepare food objects for bulk insertion
        food_objects = []
        response_list = []

        for result in gemini_results:
            if result.get('error'):
                return api_error(result['error'])  # Consider collecting all errors and returning them together

            nutrients = result['nutrients']
            food_obj = FoodItem(
                item=result['item'],
                valid=result['valid'],
                macronutrients=nutrients.get('macronutrients', []),
                vitamins=nutrients.get('vitamins', []),
                minerals=nutrients.get('minerals', []),
                other_nutrients=nutrients.get('other_nutrients', ''),
            )
            food_objects.append(food_obj)

        # Bulk insert all food items
        created_foods = FoodItem.objects.bulk_create(food_objects)

        if food_exist:
            # We have one existing food in the db
            created_foods.extend(food_item_query)

        response_obj["nutrients"] = FoodItemSerializer(created_foods, many=True).data
        return api_created_success(response_obj)
