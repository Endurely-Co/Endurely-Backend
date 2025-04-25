import unittest
from logging import raiseExceptions
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import AbstractUser

from meal.models import FoodItem
from meal.tests.factory.meal_plan_factory import MealPlanFactory
from utils.api import api_success, api_error, api_created_success
from utils.validator import Status


class FakeUser(AbstractUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_password('<PASSWORD>')


class MealPlanViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = MealPlanFactory()

    @patch('meal.views.api_success')
    @patch('meal.views.FoodItemSerializer')
    @patch('meal.views.MealPlanSerializer')
    @patch('meal.views.MealPlan.objects')
    def test_get_meal_plans_failed(self, mock_meal_plan_objs, mock_mp_serializer_class,
                                   mock_fi_serializer_class, mock_api_success):
        user_id, meal_plan_id = 2, '1'
        mock_meal_plan_qs = MagicMock()
        mock_user_by_id_qs = MagicMock()

        mock_meal_plan_objs.filter(user=user_id).return_value = mock_user_by_id_qs
        mock_meal_plan_objs.filter.return_value.filter(meal_plan_id=meal_plan_id).return_value = mock_meal_plan_qs

        mock_meal_plan_objs.filter.assert_called_with(user=user_id)

        # check meal plan
        mock_meal_plan_objs.filter(user=user_id).filter.assert_called_with(meal_plan_id=meal_plan_id)

        mock_meal_plan_serializer = MagicMock()
        mock_meal_plan_serializer.data.return_value = [
            {
                'data': 'test',
                'created_at': '2025-04-24T18:38:54.732192Z',
                'user': 2,
                'food_item': 2,
                'food_name': 'Eba and Egusi',
                'meal_plan_id': '1',
                'meal_date_time': '2025-04-24T18:38:54.732192Z'
            }
        ]
        mock_mp_serializer_class.return_value = mock_meal_plan_serializer

        mock_fi_serializer = MagicMock()
        mock_fi_serializer.data.return_value = [
            MagicMock()
        ]
        mock_fi_serializer_class.return_value = mock_fi_serializer
        mock_api_success.return_value = api_success(mock_meal_plan_serializer.data.return_value)
        response = self.factory.get_plan_by_id(user_id=user_id, plan_id=meal_plan_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'data': mock_meal_plan_serializer.data.return_value})
        mock_api_success.assert_called()


    @patch('meal.views.api_error')
    def test_no_meal_plans(self, mock_api_error):
        mock_api_error.return_value = api_error('meal_plans is absent')
        mock_request = MagicMock()
        mock_request.data.return_value = {}
        response = self.factory.add_meal_plan(mock_request.data.return_value)
        self.assertEqual(response.status_code, Status.INVALID_REQUEST)
        mock_api_error.assert_called_with('meal_plans is absent')

    @patch('meal.views.api_error')
    def test_invalid_meal_plans(self, mock_api_error):
        error_msg = 'meal_plans is not valid. Expected: list of meal plans'
        mock_api_error.return_value = api_error(error_msg)
        mock_request = MagicMock()
        mock_request.data.return_value = {'meal_plans': 'eba'}
        response = self.factory.add_meal_plan(mock_request.data.return_value)
        self.assertEqual(response.status_code, Status.INVALID_REQUEST)
        mock_api_error.assert_called_with(error_msg)

    @patch('meal.views.api_error')
    def test_meal_plan_exceed_size(self, mock_api_error):
        mock_request = MagicMock()
        error_msg = 'meal_plans too many meal plans'
        meal_plans = [{"meal": "berries", "food_item_id": i} for i in range(0, 5)]
        mock_request.data.return_value = {"user": 20,
                                          "meal_date_time": "2025-03-10T22:43:29.105481Z",
                                          "meal_plans": meal_plans
                                          }
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.add_meal_plan(mock_request.data.return_value)
        self.assertEqual(response.status_code, Status.INVALID_REQUEST)
        mock_api_error.assert_called_with(error_msg)


    @patch('meal.views.transaction')
    @patch('meal.views.User.objects')
    @patch('meal.views.FoodItem.objects')
    @patch('meal.views.api_error')
    def test_meal_plan_user_failed(self, mock_api_error, mock_fi_objs, mock_user_objs, mock_transaction):
        err_msg = "food item doesn't exist"
        mock_request = MagicMock()
        user_id = 20
        meal_plans = [{"meal": "berries", "food_item_id": i} for i in range(0, 3)]
        mock_request.data.return_value = {"user": user_id,
                                          "meal_date_time": "2025-03-10T22:43:29.105481Z",
                                          "meal_plans": meal_plans
                                          }

        mock_atomic = MagicMock()
        mock_transaction.atomic.return_value = mock_atomic

        mock_user = MagicMock()
        mock_user.get(pk=user_id).return_value = mock_user
        mock_user_objs.return_value = mock_user

        # test food doesn't exist
        mock_fi_objs.get.side_effect = FoodItem.DoesNotExist(err_msg)
        mock_api_error.return_value = api_error(err_msg)
        response = self.factory.add_meal_plan(mock_request.data.return_value)
        self.assertEqual(response.status_code, Status.INVALID_REQUEST)
        mock_api_error.assert_called_with(err_msg)


    """
    Test meal plan does not exists
    """
    @patch('meal.views.api_created_success')
    @patch('meal.views.update_or_create_meal_plan')
    @patch('meal.views.transaction')
    @patch('meal.views.User.objects')
    @patch('meal.views.FoodItem.objects')
    @patch('meal.views.MealPlan.objects.filter')
    def test_post_meal_plan_not_exist(self, mock_meal_plan_filter, mock_fi_objs, mock_user_objs,
                            mock_transaction, mock_update_or_create_meal_plan,
                            mock_api_created_success):
        success_res = {"message": "Meal plan added successfully"}
        mock_request = MagicMock()
        user_id = 20
        meal_plans = [{"meal": "berries", "food_item_id": i} for i in range(0, 3)]
        mock_request.data.return_value = {"user":user_id ,
                                          "meal_date_time": "2025-03-10T22:43:29.105481Z",
                                          "meal_plans": meal_plans
                                          }
        # Provide values for mocks
        mock_user_objs.get.return_value = user_id
        mock_fi_objs.get.return_value = 3

        mock_atomic = MagicMock()
        mock_transaction.atomic.return_value = mock_atomic
        mock_api_created_success.return_value = api_created_success(success_res)

        mock_meal_plan = mock_meal_plan_filter.return_value
        mock_meal_plan.exists.return_value = False

        # Test meal already exists
        mock_update_or_create_meal_plan.return_value =None
        response = self.factory.add_meal_plan(mock_request.data.return_value)
        mock_update_or_create_meal_plan.assert_called_with('012', user_id,
                                                           mock_request.data.return_value['meal_date_time'],
                                                           mock_fi_objs.get.return_value)
        mock_transaction.atomic.assert_called()
        mock_api_created_success.assert_called_with(success_res)
        self.assertEqual(response.status_code, Status.CREATED_SUCCESS)
        self.assertEqual(response.data, {'data': success_res})


    """
    Test meal plan already exists
    """
    @patch('meal.views.api_created_success')
    @patch('meal.views.transaction')
    @patch('meal.views.User.objects')
    @patch('meal.views.FoodItem.objects')
    @patch('meal.views.MealPlan.objects.filter')
    def test_post_meal_plan_meal_exist(self, mock_meal_plan_filter, mock_fi_objs, mock_user_objs,
                            mock_transaction, mock_api_created_success):
        success_res = {"message": "Meal plan added successfully"}
        mock_request = MagicMock()
        user_id = 20
        meal_plans = [{"meal": "berries", "food_item_id": i} for i in range(0, 3)]
        mock_request.data.return_value = {"user":user_id ,
                                          "meal_date_time": "2025-03-10T22:43:29.105481Z",
                                          "meal_plans": meal_plans
                                          }
        # Provide values for mocks
        mock_user_objs.get.return_value = user_id
        mock_fi_objs.get.return_value = 3

        mock_atomic = MagicMock()
        mock_transaction.atomic.return_value = mock_atomic
        mock_api_created_success.return_value = api_created_success(success_res)

        mock_meal_plan = mock_meal_plan_filter.return_value
        mock_meal_plan.exists.return_value = True

        response = self.factory.add_meal_plan(mock_request.data.return_value)

        mock_transaction.atomic.assert_called()
        mock_api_created_success.assert_called_with(success_res)
        self.assertEqual(response.status_code, Status.CREATED_SUCCESS)
        self.assertEqual(response.data, {'data': success_res})
        self.assertTrue(mock_meal_plan.exists())

    @patch('meal.views.api_error')
    def test_delete_meal_plan(self, mock_api_error):
        user_id, plan_id = 22, 2
        mock_api_error.return_value = api_error('plan_id is required')
        response = self.factory.delete_meal_plan('', user_id)
        # check that api_error is called
        mock_api_error.assert_called_with('plan_id is required')
        self.assertEqual(response.status_code, Status.INVALID_REQUEST)

    @patch('meal.views.api_error')
    def test_delete_meal_plan_empty_plan_id(self, mock_api_error):
        user_id, plan_id = 22, None
        mock_api_error.return_value = api_error('plan_id is required')
        response = self.factory.delete_meal_plan('', user_id)
        # check that api_error is called
        mock_api_error.assert_called_with('plan_id is required')
        self.assertEqual(response.status_code, Status.INVALID_REQUEST)

    def doCleanups(self):
        self.factory.tear_down()
