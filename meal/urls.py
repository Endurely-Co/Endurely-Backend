"""
URL configuration for fitfocus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from meal import views

urlpatterns = [
    path('plan', views.MealPlanView.as_view(), name="meal-goals"),
    path('plan/<int:user_id>', views.MealPlanView.as_view(), name="meal-goals"),
    path('plan', views.MealPlanView.as_view(), name="meal-goals"),
    path('recommendations', views.MealRecommendationView.as_view(), name="meal-recommendations"),
    path('recommendations/new', views.MealRecommendationView.as_view(), name="meal-recommendations-add"),
    path('nutrients', views.NutritionView.as_view(), name="nutrition-suggestions")
    #MealRecommendationView
    # NutritionView

]
