import unittest
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from meal.tests.factory.nutrient_factory import NutrientFactory
from utils.api import api_success, api_error, api_created_success


class TestCaseNutrient(unittest.TestCase):

    def setUp(self):
        self.factory = NutrientFactory()

    @patch('meal.views.api_created_success')
    @patch('meal.views.FoodItem.objects')
    @patch('meal.views.transaction')
    @patch('meal.views.User.objects')
    @patch('meal.views.GeminiApi')
    def test_add_nutrient_food_not_in_db(self, mock_gemini, mock_user_objs, mock_transaction,
                                             mock_food_item_objs, mock_api_created_success):
        mock_transaction.atomic.return_value = MagicMock()
        mock_request = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 2
        mock_user_objs.get.return_value = mock_user
        mock_request.data = {
            'meal': 'Eba, egusi',
            'user': 2,
        }
        fake_response = {
            "user": mock_user.id,
            'nutrients': []
        }

        mock_food_item_objs.filter.return_value = MagicMock()
        mock_food_item_objs.exists.return_value = False
        mock_api_created_success.return_value = api_created_success(fake_response)
        response = self.factory.add_nutrients(mock_request.data)
        mock_api_created_success.assert_called_with(fake_response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'data': fake_response})


    @patch('meal.views.api_created_success')
    @patch('meal.views.FoodItem.objects')
    @patch('meal.views.transaction')
    @patch('meal.views.User.objects')
    @patch('meal.views.GeminiApi')
    def test_add_nutrient_food_already_in_db(self, _, mock_user_objs, mock_transaction,
                                             mock_food_item_objs, mock_api_created_success):
        mock_transaction.atomic.return_value = MagicMock()
        mock_request = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 2
        mock_user_objs.get.return_value = mock_user
        mock_request.data = {
            'meal': 'Eba, egusi',
            'user': 2,
        }
        fake_response = {
                "user": mock_user.id,
            'nutrients': []
            }

        mock_food_item_objs.filter.return_value = MagicMock()
        mock_food_item_objs.exists.return_value = True
        mock_api_created_success.return_value = api_created_success(fake_response)
        response = self.factory.add_nutrients(mock_request.data)
        mock_api_created_success.assert_called_with(fake_response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'data': fake_response})

    @patch('meal.views.User.objects')
    @patch('meal.views.GeminiApi')
    @patch('meal.views.api_error')
    def test_add_nutrient_invalid_user(self, mock_api_error, _, mock_user_objs):
        error_msg = "User does not exist"
        mock_request = MagicMock()
        mock_request.data = {
            'meal': 'Eba, egusi',
            'user': 2,
        }
        mock_api_error.return_value = api_error(error_msg)
        mock_user_objs.get.side_effect = User.DoesNotExist(error_msg)

        response = self.factory.add_nutrients(mock_request.data)
        mock_api_error.assert_called_with(error_msg)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'code': 400, 'message': error_msg})

    @patch('meal.views.GeminiApi')
    @patch('meal.views.api_error')
    def test_add_nutrient_food_exceed_size(self, mock_api_error, _):
        error_msg = "Maximum of two food/drink is allowed!"
        mock_request = MagicMock()
        mock_request.data = {
            'meal': 'Eba, beans, egusi',
            'user': 2,
        }
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.add_nutrients(mock_request.data)
        mock_api_error.assert_called_with(error_msg)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'code': 400, 'message': error_msg})


    @patch('meal.views.GeminiApi')
    @patch('meal.views.api_error')
    def test_add_nutrient_food_error(self, mock_api_error, mock_gemini_api):
        error_msg = "Food/drink is invalid. Try again!"
        mock_request = MagicMock()
        mock_request.data = {
            'meal': 'Ea',
            'user': 2,
        }
        mock_gemini_api.return_value = MagicMock()
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.add_nutrients(mock_request.data)
        mock_api_error.assert_called_with(error_msg)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'code': 400, 'message': error_msg})


    """
    user and meal are required
    """
    @patch('meal.views.GeminiApi')
    @patch('meal.views.api_error')
    def test_add_new_nutrient_user_meal_error(self, mock_api_error, mock_gemini_api):
        msg_error = "user and meal are required"
        mock_request = MagicMock()
        mock_request.data.return_value = {}
        mock_api_error.return_value = api_error(msg_error)
        response = self.factory.add_nutrients(None)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'code': 400, 'message': msg_error})
        mock_api_error.assert_called_with(msg_error)

    @patch('meal.views.GeminiApi')
    @patch('meal.views.api_success')
    @patch('meal.views.MealPlanSerializer')
    @patch('meal.views.MealPlan.objects')
    def test_get_nutrient_by_id(self, mock_meal_plan_objs, mock_mp_serializer_class,
                                mock_api_success, mock_gemini_api):
        user_id = 2
        mock_meal_plan_objs.filter.return_value = [MagicMock()]
        mock_mp_serializer = MagicMock()
        mock_mp_serializer.data = [
            {
                'data': 'test',
                'created_at': '2025-04-24T18:38:54.732192Z',
                'user': i,
                'food_item': 2,
                'food_name': 'Eba and Egusi',
                'meal_plan_id': '1',
                'meal_date_time': '2025-04-24T18:38:54.732192Z'
            } for i in range(0, 2)
        ]
        mock_mp_serializer_class.return_value = mock_mp_serializer
        mock_api_success.return_value = api_success(mock_mp_serializer.data)
        mock_gemini_api.return_value = MagicMock()
        response = self.factory.get_nutrients(user_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'data': mock_mp_serializer.data})
        mock_api_success.assert_called_with(mock_mp_serializer.data)