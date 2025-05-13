from rest_framework.test import APIRequestFactory

from routines.views import FitnessRoutineView


class FitnessRoutineViewFactory(APIRequestFactory):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view = FitnessRoutineView.as_view()


    def add_exercise(self, exercise):
        request = self.post("/add", data=exercise)
        return self.view(request)

    def get_view(self):
        return self.view()