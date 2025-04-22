from rest_framework.test import RequestsClient

client = RequestsClient()
response = client.get('http://127.0.0.1:8000/onboarding/')
assert response.status_code == 200
