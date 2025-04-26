from rest_framework.test import APIRequestFactory

from onboarding.views import CreateAccountView


class CreateAcctFactory(APIRequestFactory):

    def __init__(self, **defaults):
        self.base_path = "/create-user"
        self.view = CreateAccountView.as_view()
        super().__init__(**defaults)

    def create_acct(self, data):
        request = self.post(self.base_path, data=data)
        return self.view(request)
