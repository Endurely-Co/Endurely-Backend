from rest_framework.test import APIRequestFactory

from meal.views import NutrientView


class NutrientFactory(APIRequestFactory):

    def __init__(self, **defaults):
        super().__init__(**defaults)
        self.base_path = "/nutrient"
        self.view = NutrientView.as_view()


    def get_nutrients(self, user_id):
        request = self.get(self.base_path)
        return self.view(request, user_id)

    def add_nutrients(self, data):
        request = self.post(self.base_path, data=data)
        return self.view(request)