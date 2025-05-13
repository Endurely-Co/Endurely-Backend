from django.contrib.auth.models import User
from django.db import transaction

from meal.models import MealPlan, MealInfo, FoodItem
from meal.serializers import MealPlanSerializer, MealInfoSerializer, FoodItemSerializer
from utils.api import api_created_success, api_error, api_success
from utils.api_ext import AuthenticatedAPIView
from utils.fitmodels import update_or_create_meal_plan
from utils.gemini import GeminiApi


# Create your views here.

# deprecated
class MealRecommendationView(AuthenticatedAPIView):

    def get(self, _):
        try:
            meal_data = MealInfo.objects.all()
            serializer = MealInfoSerializer(meal_data, many=True)
            return api_success(serializer.data)
        except Exception as err:
            return api_error('Invalid server error')

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
            try:
                meal_plan = MealPlan.objects.filter(meal_plan_id=meal_to_delete, user=user_id)
                meal_plan.delete()
                return api_success("Meal plan successfully deleted")
            except Exception as err:
                return api_error('Invalid server error')
        return api_error("plan_id is required")

    # meal, calorie rm -rf mealplan/migrations
    def post(self, request, *args, **kwargs):
        meal_plans = request.data.get('meal_plans')
        if not meal_plans:
            return api_error("meal_plans is absent")

        if type(meal_plans) is not list:
            return api_error("meal_plans is not valid. Expected: list of meal plans")

        if len(meal_plans) > 4:
            return api_error("meal_plans too many meal plans")
        plan_id = "".join(sorted([str(mp['food_item_id']) for mp in meal_plans]))

        try:
            user = User.objects.get(pk=request.data['user'])
        except User.DoesNotExist:
            return api_error("User does not exist")

        success_msg = []
        with transaction.atomic():
            for plan in meal_plans:
                try:
                    food_item = FoodItem.objects.get(pk=plan['food_item_id'])
                except FoodItem.DoesNotExist:
                    return api_error("food item doesn't exist")

                created = True
                try:
                    meal_plan = MealPlan.objects.get(meal_plan_id=plan['food_item_id'], user=user)
                except MealPlan.DoesNotExist:
                    meal_plan, created = update_or_create_meal_plan(plan_id, user, request.data['meal_date_time'], food_item)

        if created:
            return api_created_success({"message": "Meal plan added successfully"})
        return api_error("Meal plan was not added. Please try again later")


class NutrientView(AuthenticatedAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = GeminiApi()

    def get(self, _, user_id):
        meal_plan = MealPlan.objects.filter(user=user_id)
        meal_plan_data = MealPlanSerializer(meal_plan, many=True).data
        for i in range(len(meal_plan)):
            serialized_food = FoodItemSerializer(meal_plan[i].food_item).data
            meal_plan_data[i]['other_nutrients'] = serialized_food['other_nutrients']
            # meal_plan_data[i]["nutrients"] = serialized_food
            # print("food_item", )
        return api_success(meal_plan_data)


    def post(self, request):
        if not request.data.get('meal') or not request.data.get('user'):
            return api_error("user and meal are required")

        foods = request.data.get('meal').lower().strip()

        if not foods or len(foods) <= 2:
            return api_error("Food/drink is invalid. Try again!")

        food_items = [item for item in foods.split(',')]

        if len(food_items) > 2:
            return api_error("Maximum of two food/drink is allowed!")

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
            if len(food_item_query) >= len(food_items):
                response_obj["nutrients"] = FoodItemSerializer(food_item_query, many=True).data
                return api_created_success(response_obj)
            else:
                for food in food_items:
                    if food not in [f.item for f in food_item_query]:
                        foods = food

        # Get results from gemini API
        gemini_results = self.gemini.nutrients_from_food(foods)['results']

        food_objects = []

        for result in gemini_results:
            if result.get('error'):
                return api_error(result['error'])

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
        with transaction.atomic():
            # Bulk insert all food items
            created_foods = FoodItem.objects.bulk_create(food_objects)

        if food_exist:
            # We have one existing food in the db
            created_foods.extend(food_item_query)

        response_obj["nutrients"] = FoodItemSerializer(created_foods, many=True).data
        return api_created_success(response_obj)
