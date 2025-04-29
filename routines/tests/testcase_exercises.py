import unittest
from unittest.mock import patch, MagicMock

from utils.api import api_error, api_success
from .factory.exercise_factory import ExerciseFactory


class TestCaseExercises(unittest.TestCase):

    def setUp(self):
        self.factory = ExerciseFactory()

    @patch('routines.views.api_error')
    @patch('routines.views.Exercise.objects')
    def test_get_exercise_error(self, mock_exercise_objs, mock_api_error):
        error_msg = 'Invalid server error'
        mock_exercise_objs.all.side_effect = Exception(error_msg)
        mock_api_error.return_value = api_error(error_msg)
        response = self.factory.get_exercises()
        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': error_msg, 'code': 400}, response.data)
        mock_api_error.assert_called_with(error_msg)


    @patch('routines.views.api_success')
    @patch('routines.views.GetExercisesSerializer')
    @patch('routines.views.Exercise.objects')
    def test_get_exercise_success(self, mock_exercise_objs, mock_get_exercises_serializer, mock_api_success):
        mock_exercise_objs.all.return_value = MagicMock()
        mock_exercise_objs.all.return_value.order_by.return_value = MagicMock()
        fake_response = [
        {
            "id": 194,
            "key": "RUN01",
            "name": "Running",
            "description": "1. Maintain a steady pace with proper posture.\n2. Control your breathing.\n3. Adjust speed based on endurance goals.",
            "category": "CM"
        }]
        mock_api_success.return_value = api_success(fake_response)
        mock_get_exercises_serializer.data.return_value = fake_response
        response = self.factory.get_exercises()
        self.assertEqual(200, response.status_code)
        self.assertEqual({'data': fake_response}, response.data)
        mock_exercise_objs.all.return_value.order_by.assert_called()