from django.urls import path

from utils.invalid_json_view import InvalidJsonView
from . import views

urlpatterns = [
    path("", InvalidJsonView.as_view(), name="not-valid"),
    path("exercises", views.GetExercises.as_view(), name="get-exercises"),
    # path("exercises/categories", views.GetCategories.as_view(), name="get-categories"),
    path("add", views.FitnessRoutineView.as_view(), name="fitness-routine-add"),
    path("user/<int:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-all"),
    path("<int:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-remove"),
    # path("exercises/category/<str:category>", views.GetExercisesByCategory.as_view(), name="get-exercises-by category")
]
