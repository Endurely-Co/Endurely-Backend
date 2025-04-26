import unittest
from unittest.mock import patch, MagicMock

from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from meal.serializers import MealInfoSerializer, required
from meal.views import MealRecommendationView
from utils.api import api_created_success, api_error
from utils.validator import Status


def _build_recommendation_factory_get():
    factory = APIRequestFactory()
    request = factory.get("/recommendations")
    view = MealRecommendationView.as_view()
    return view(request)


def _build_recommendation_factory_post(mock_request):
    factory = APIRequestFactory()
    request = factory.post('/recommendations/new', data=mock_request)
    view = MealRecommendationView.as_view()
    return view(request)


class FakeMealInfoSerializer(MealInfoSerializer):
    class Meta(MealInfoSerializer.Meta):
        fields = '__all__'
        extra_kwargs = {'meal': required, 'calorie': required}


class MealRecommendationTestCase(unittest.TestCase):

    @patch('meal.views.api_created_success')
    @patch('meal.views.MealInfoSerializer')
    def test_post_meal_plan_success(self, mock_serializer_class, mock_api_created):
        mock_request = {
            'meal': 'Eba and Egusi',
            'calorie': 2.4
        }

        mock_serializer = MagicMock()
        mock_serializer.is_valid.return_value = True
        mock_serializer_class.return_value = mock_serializer
        mock_serializer_class.save.return_value = None
        mock_response = {
            "id": 68,
            "meal": "Rice",
            "calorie": 21.2,
            "created_at": "2025-04-24T18:38:54.732192Z"
        }
        mock_serializer_class.data = mock_response

        # 'recommendations/new'
        mock_api_created.return_value = api_created_success(mock_serializer_class.data)

        response = _build_recommendation_factory_post(mock_request)

        self.assertEqual(response.data, {'data': mock_response})
        self.assertEqual(response.status_code, 201)
        mock_api_created.assert_called()

    @patch('meal.views.api_error')
    @patch('meal.views.MealInfoSerializer')
    def test_post_meal_plan_error(self, mock_serializer_class, mock_api_error):
        mock_request = {
            'meal': 'Eba and Egusi',
        }

        # Test bad request
        mock_api_error.return_value = api_error('Bad request')
        mock_serializer_class.return_value = FakeMealInfoSerializer(data=mock_request)
        response = _build_recommendation_factory_post(mock_request)
        # check that api_error is called
        mock_api_error.assert_called()

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
        _build_recommendation_factory_get()
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

        response = _build_recommendation_factory_get()
        mock_api_success.assert_called_once_with(expected_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"data": expected_data})

    @patch('utils.api.Response')
    def test_api_success(self, mock_response):
        value = [{"foo": "bar"}]
        from meal.views import api_success

        api_success(value)
        mock_response.assert_called_once_with(data={'data': value}, status=200)
