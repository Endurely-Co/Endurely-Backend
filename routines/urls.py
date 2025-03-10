from django.urls import path
from . import views

urlpatterns = [
    path("exercises", views.GetExercises.as_view(), name="get-exercises"),
    path("exercises/categories", views.GetCategories.as_view(), name="get-categories"),
    path("add", views.FitnessRoutineView.as_view(), name="fitness-routine-add"),
    #path("update/<int:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-update"),
    path("user/<int:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-all"),
    path("<int:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-remove"),
    #path("nutrients", views.NutritionView.as_view(), name="food-nutrients"),
    path("exercises/category/<str:category>", views.GetExercisesByCategory.as_view(), name="get-exercises-by category")
]
