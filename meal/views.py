from django.contrib.auth.models import User
from django.db import transaction
from django.utils.timezone import now

from meal.models import MealPlan, MealInfo
from meal.serializers import MealPlanSerializer, MealInfoSerializer
from routines.models import NutritionInfo
from utils.api import api_created_success, api_error, api_success
from utils.api_ext import AuthenticatedAPIView


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
        print('request', request, user_id)
        meal_plan = MealPlan.objects.filter(user=user_id)
        serializer = MealPlanSerializer(meal_plan)
        return api_success(serializer.data)

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
