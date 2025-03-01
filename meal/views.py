from django.contrib.auth.models import User
from django.utils.timezone import now

from meal.models import MealPlan, MealInfo
from meal.serializers import MealPlanSerializer, MealInfoSerializer
from utils.api import api_created_success, api_error, api_success
from utils.api_ext import AuthenticatedAPIView


# Create your views here.

class MealRecommendationView(AuthenticatedAPIView):

    def get(self, _):
        meal_data = MealInfo.objects.all()
        serializer = MealInfoSerializer(meal_data, many=True)
        return api_created_success(serializer.data)

    def post(self, request, *args, **kwargs):
        pass


class MealPlanView(AuthenticatedAPIView):

    def get(self, request, user_id):
        print('request', request, user_id)
        meal_plan = MealPlan.objects.filter(user=user_id)
        serializer = MealPlanSerializer(meal_plan)
        return api_success(serializer.data)

    # meal, calorie rm -rf mealplan/migrations
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get_by_natural_key(request.data['username'])
            meal_info = MealInfo(meal=request.data['meal'],
                                 calorie=request.data['calorie'],
                                 created_at=now())
            meal_info.save()
            meal_plan = MealPlan(created_at=now(), user=user,
                                 meal=meal_info)
            meal_plan.save()
            return api_created_success(MealInfoSerializer(meal_info).data)
        except KeyError as kerr:
            return api_error(f"{str(kerr)} is missing")
        except User.DoesNotExist as dne:
            return api_error(str(dne))

