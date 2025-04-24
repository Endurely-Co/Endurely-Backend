import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase
from meal.views import MealRecommendationView
import pytest

from utils.api import api_success
from utils.validator import Status


def create_recommendation_factory():
    factory = APIRequestFactory()
    request = factory.get("/recommendations")
    view = MealRecommendationView.as_view()
    return view(request)


class MealRecommendationTestCase(unittest.TestCase):

    @patch('meal.views.api_error')
    @patch('meal.views.MealInfo')
    def test_get_meal_plan_failed(self, mock_mp_model, mock_api_error):
        expected_err_msg = 'Invalid server error'

        mock_meal_plan = Exception(expected_err_msg)
        mock_mp_model.objects.all.return_value = [mock_meal_plan]

        mock_api_error.return_value = Response(status=Status.INVALID_REQUEST, data={
            'code': Status.INVALID_REQUEST,
            'message': expected_err_msg
        })

        response = create_recommendation_factory()

        mock_api_error.assert_called_once_with(expected_err_msg)

    @patch("meal.views.api_success")
    @patch("meal.views.MealInfo")
    @patch("meal.views.MealInfoSerializer")
    def test_get_meal_plan_success(self, mock_serializer_class, mock_meal_model, mock_api_success):
        # Mock meal instance
        mock_instance = MagicMock()
        mock_meal_model.objects.all.return_value = [mock_instance]

        mock_serializer_instance = MagicMock()
        expected_data = [
            {
                "id": 2,
                "meal": "Scrambled Eggs with Spinach",
                "calorie": 300.0,
                "created_at": "2025-04-23T12:00:00Z"
            }
        ]
        mock_serializer_instance.data = expected_data
        mock_serializer_class.return_value = mock_serializer_instance

        mock_api_success.return_value = Response(data={"data": expected_data}, status=200)

        response = create_recommendation_factory()
        mock_api_success.assert_called_once_with(expected_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"data": expected_data})

    @patch('utils.api.Response')
    def test_api_success(self, mock_response):
        value = [{"foo": "bar"}]
        from meal.views import api_success

        api_success(value)
        mock_response.assert_called_once_with(data={'data': value}, status=200)
