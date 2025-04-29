from rest_framework.test import APIRequestFactory

from routines.views import GetExercises


class ExerciseFactory(APIRequestFactory):


    def __init__(self, **defaults):
        super().__init__(**defaults)
        self.base_path = "/exercises"
        self.view = GetExercises.as_view()

    def get_exercises(self):
        request = self.get("/exercises")
        return self.view(request)