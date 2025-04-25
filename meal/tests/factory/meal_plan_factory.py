from rest_framework.test import APIRequestFactory

from meal.views import MealPlanView


class MealPlanFactory:

    def __init__(self):
        self.base_path = "/plan"
        self.factory = APIRequestFactory()
        self.view = MealPlanView.as_view()

    def get_plans(self):
        request = self.factory.get(self.base_path)
        return self.view(request)

    def get_plan_by_id(self, user_id, plan_id):
        request = self.factory.get(f"{self.base_path}", {'plan_id': plan_id})
        return self.view(request, user_id=user_id)

    def add_meal_plan(self, data):
        request = self.factory.post(self.base_path, data=data)
        return self.view(request)

    def delete_meal_plan(self, plan_id, user_id):
        request = self.factory.delete(f'{self.base_path}?plan_id={plan_id}')
        return self.view(request, user_id)


    def tear_down(self):
        self.factory = None

    # def _build_recommendation_factory_get():
    #     factory = APIRequestFactory()
    #     request = factory.get("/recommendations")
    #     view = MealRecommendationView.as_view()
    #     return view(request)
