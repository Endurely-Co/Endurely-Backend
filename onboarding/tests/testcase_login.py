import unittest
from unittest.mock import patch, MagicMock

from onboarding.tests.factory.login_factory import LoginFactory
from utils.api import api_created_success, api_error


class LoginTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = LoginFactory()

    @patch('onboarding.views.api_created_success')
    @patch('onboarding.views.get_tokens_for_user')
    @patch('onboarding.views.authenticate')
    def test_login_success(self, mock_authenticate, mock_get_tokens_for_user, mock_api_created_success):
        login_request = {
            "username": "john",
            "password": "12ABc$f"
        }
        mock_get_tokens_for_user.return_value = {
            'access': 'test_access',
            'refresh': 'test_refresh'
        }

        mock_user = MagicMock()
        mock_user.id = 12
        mock_user.username = "john"
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.email = 'test@gm.com'
        mock_api_created_success.return_value = api_created_success(
            {
                "user_id": mock_user.id,
                "username": mock_user.username,
                "first_name": mock_user.first_name,
                "last_name": mock_user.last_name,
                "email": mock_user.email,
                "token": mock_get_tokens_for_user.return_value['access'],
                "refresh_token": mock_get_tokens_for_user.return_value['refresh']
            }
        )
        mock_authenticate.return_value = mock_user
        response = self.factory.login(login_request)
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data, mock_api_created_success.return_value.data)
        mock_authenticate.assert_called_with(username=login_request['username'], password=login_request['password'])
        mock_get_tokens_for_user.assert_called_with(mock_user)
        mock_api_created_success.assert_called_with(
            {
                "user_id": mock_user.id,
                "username": mock_user.username,
                "first_name": mock_user.first_name,
                "last_name": mock_user.last_name,
                "email": mock_user.email,
                "token": mock_get_tokens_for_user.return_value['access'],
                "refresh_token": mock_get_tokens_for_user.return_value['refresh']
            }
        )


    @patch('onboarding.views.api_error')
    def test_login_required_username_or_password_failed(self, mock_api_error):
        error_msg = "Username and password are required"
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.login({
            "username": "john"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, mock_api_error.return_value.data)
        mock_api_error.assert_called_with(error_msg)

    @patch('onboarding.views.api_error')
    @patch('onboarding.views.authenticate')
    def test_login_invalid_user_password_error(self, mock_authenticate, mock_api_error):
        error_msg = "Invalid username or password"
        mock_api_error.return_value = api_error(error_msg)
        mock_authenticate.return_value = None
        response = self.factory.login({
            "password": "12ABc$f",
            "username": "john"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, mock_api_error.return_value.data)
        mock_authenticate.assert_called_with(username="john", password="12ABc$f")
        mock_api_error.assert_called_with(error_msg)