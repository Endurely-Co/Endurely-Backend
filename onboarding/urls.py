from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("create-account", views.CreateAccountView.as_view(), name="create-user"),
    path("login", views.LoginView.as_view(), name="login-user"),
    path("refresh-token", TokenRefreshView.as_view(), name="token-refresh"),
    path("generate-otp", views.CreateGetOTPView().as_view()),
    path("validate-otp", views.ValidateOTPView().as_view())
]