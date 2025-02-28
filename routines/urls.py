from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("exercises", views.GetExercises.as_view(), name="get-exercises"),
    path("exercises/categories", views.GetCategories.as_view(), name="get-categories"),
    path("add", views.FitnessRoutineView.as_view(), name="fitness-routine-add"),
    path("update/<str:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-update"),
    path("all", views.FitnessRoutineView.as_view(), name="fitness-routine-all"),
    path("delete/<str:pk>", views.FitnessRoutineView.as_view(), name="fitness-routine-remove"),
    path("exercises/category/<str:category>", views.GetExercisesByCategory.as_view(), name="get-exercises-by category")
]
