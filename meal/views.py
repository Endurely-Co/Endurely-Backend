from django.contrib.auth.models import User
from django.db import transaction
from django.utils.timezone import now

from meal.models import MealPlan, MealInfo, NutritionInfo, FoodItem
from meal.serializers import MealPlanSerializer, MealInfoSerializer, NutritionSerializer, FoodItemSerializer
from utils.api import api_created_success, api_error, api_success
from utils.api_ext import AuthenticatedAPIView
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
        meal_plan = MealPlan.objects.filter(user=user_id)
        response = []
        # response = MealPlanSerializer(meal_plan, many=True).data
        for plan in meal_plan:
            response.append({"created_at": plan.created_at,
                             "id": plan.id,
                             "meal": MealInfoSerializer(plan.meal).data,
                             "nutrient": NutritionSerializer(plan.nutrient).data
                             })
        return api_success(response)

    # meal, calorie rm -rf mealplan/migrations
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        nutrient = None
        try:
            user = User.objects.get_by_natural_key(request.data['username'])

            nutrient_data = request.data.get('nutrients')

            if type(nutrient_data) is list:
                nutrients = []
                db_result, meal_info = {}, None
                for nutrition in nutrient_data:
                    meal_info = MealInfo(meal=request.data['meal'],
                                         calorie=request.data['calorie'],
                                         created_at=now())
                    nutrient = NutritionInfo(created_at=now(), nutrient=nutrition,
                                             food_name=request.data['meal'],
                                             user=user)
                    nutrient.save()
                    meal_info.save()
                    meal_plan = MealPlan(created_at=now(), user=user,
                                         meal=meal_info,
                                         nutrient=nutrient)
                    meal_plan.save()
                    nutrients.append({
                        "name": nutrition,
                        "'id": nutrient.id
                    })
                db_result = MealInfoSerializer(meal_info).data
                db_result['nutrients'] = nutrients
                return api_created_success(db_result)
            else:
                raise KeyError(f"nutrients type of list was expected but {type(nutrient_data)} is giving")
        except KeyError as kerr:
            return api_error(f"{str(kerr)} is missing")
        except User.DoesNotExist as dne:
            return api_error(str(dne))


class NutritionView(AuthenticatedAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = GeminiApi()

    from django.db import transaction

    @transaction.atomic
    def post(self, request):
        foods = request.data.get('food_name').lower().strip()

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

        for food_item in created_foods:
            MealPlan.objects.update_or_create(
                id=food_item.id,
                user=user,
                food_item=food_item,
                food_name=food_item.item
            )
        response_obj["nutrients"] = FoodItemSerializer(created_foods, many=True).data
        return api_created_success(response_obj)
