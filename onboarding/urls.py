from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

from .views import Logout

urlpatterns = [
    path("create-account", views.CreateAccountView.as_view(), name="create-user"),
    path("login", views.LoginView.as_view(), name="login-user"),
    path("refresh-token", TokenRefreshView.as_view(), name="token-refresh"),
    path('logout/', Logout.as_view()),

]
