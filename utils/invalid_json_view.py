from rest_framework.views import APIView

from utils.api import api_error


class InvalidJsonView(APIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.error_msg = api_error("Invalid path")

    def get(self, _):
        return self.error_msg



