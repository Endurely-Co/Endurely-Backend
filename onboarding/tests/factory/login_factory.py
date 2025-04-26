from rest_framework.test import APIRequestFactory

from onboarding.views import LoginView

class LoginFactory(APIRequestFactory):
    
    def __init__(self, **defaults):
        self.base_path = "/login"
        self.view = LoginView.as_view()
        super().__init__(**defaults)

    def login(self, data):
        request = self.post(self.base_path, data=data)
        return self.view(request)
