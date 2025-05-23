import unittest
from unittest.mock import patch, MagicMock

from django.db import IntegrityError

from onboarding.tests.factory.create_acct_factory import CreateAcctFactory
from utils.api import api_error, api_created_success


class CreateAccountTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = CreateAcctFactory()


    @patch('onboarding.views.api_error')
    def test_invalid_request_type(self, mock_api_error):
        error_msg = "Invalid request type"
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.create_acct(["some data"])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, mock_api_error.return_value.data)
        mock_api_error.assert_called_with(error_msg)


    @patch('onboarding.views.User.objects')
    @patch('onboarding.views.api_error')
    def test_missing_required_field(self, mock_api_error, mock_user_objs):
        error_msg = "'first_name' is missing"
        mock_user_objs.create_user.side_effect = KeyError(error_msg)
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.create_acct({
            "username": "john",
            "password": "12ABc$f",
            "last_name": "Doe",
            'email': 'john@gm.com'
        })

        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': error_msg}, response.data)
        mock_api_error.assert_called_with(error_msg)


    @patch('onboarding.views.User.objects')
    @patch('onboarding.views.api_error')
    def test_username_already_exists(self, mock_api_error, mock_user_objs):
        error_msg = "Username already exist. Please try again"
        mock_user_objs.create_user.side_effect = IntegrityError(error_msg)
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.create_acct({
            "username": "john",
            "password": "12ABc$f",
            "first_name": "John",
            "last_name": "Doe",
            'email': 'john@gm.com'
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': error_msg}, response.data)
        mock_api_error.assert_called_with(error_msg)


    @patch('onboarding.views.User.objects')
    @patch('onboarding.views.api_error')
    def test_weak_password_error(self, mock_api_error, mock_user_objs):
        error_msg = ("Password is too weak. Use a strong password with at least 6"
                     " upper and lower case alpha-numeric characters including special symbols")
        mock_user_objs.create_user.return_value = MagicMock()
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.create_acct({
            "first_name": "John",
            "username": "john",
            "password": "123456",
            "last_name": "Doe",
            'email': 'john@gm.com'
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': error_msg}, response.data)
        mock_api_error.assert_called_with(error_msg)


    @patch('onboarding.views.User.objects')
    @patch('onboarding.views.api_error')
    def test_invalid_username_or_email(self, mock_api_error, mock_user_objs):
        error_msg = "Invalid email or username"
        mock_user_objs.create_user.return_value = MagicMock()
        mock_api_error.return_value = api_error(error_msg)

        fake_request = {
            "first_name": "John",
            "username": "12john",
            "password": "123456",
            "last_name": "Doe",
            'email': 'john@gm.com'
        }

        # check invalid username
        response = self.factory.create_acct(fake_request)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': error_msg}, response.data)
        mock_api_error.assert_called_with(error_msg)

        # check invalid email
        fake_request['username'] = "john"
        fake_request['email'] = "john@gm"
        response = self.factory.create_acct(fake_request)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': error_msg}, response.data)
        mock_api_error.assert_called_with(error_msg)


    @patch('onboarding.views.api_created_success')
    @patch('onboarding.views.User.objects')
    def test_create_account_success(self, mock_user_objs, mock_api_created_success):

        mock_user = MagicMock()
        mock_user.id = 12
        mock_user.username = "john"
        mock_user.first_name = "John"
        mock_user.last_name = "Doe"
        mock_user.acct_type = 'verify'
        mock_user.email = 'john@gm.com'
        mock_user_objs.create_user.return_value = mock_user
        fake_response = {
            "username": mock_user.username,
            "first_name": mock_user.first_name,
            "last_name": mock_user.last_name,
            "email": mock_user.email,
            "acct_type": mock_user.acct_type
        }
        mock_api_created_success.return_value = api_created_success(fake_response)
        fake_request = {
            "first_name": "John",
            "username": "john",
            "password": "1Ab!456",
            "last_name": "Doe",
            'email': 'john@gm.com'
        }

        response = self.factory.create_acct(fake_request)
        mock_user_objs.save.return_value = None

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data, mock_api_created_success.return_value.data)
        mock_user_objs.create_user.assert_called_with(
            username=fake_request['username'],
            password=fake_request['password'],
            email=fake_request['email']
        )



