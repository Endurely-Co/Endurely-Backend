import unittest
from unittest.mock import patch, MagicMock

from django.http import Http404

from utils.api import api_error, api_success, api_created_success
from .factory.exercise_factory import ExerciseFactory
from .factory.routine_factory import FitnessRoutineViewFactory
from routines.views import FitnessRoutineView
from ..models import FitnessRoutine


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


class TestCaseFitnessRoutine(unittest.TestCase):

    def setUp(self):
        self.factory = FitnessRoutineViewFactory()

    @patch('routines.views.api_error')
    @patch('routines.views.transaction')
    @patch('routines.views.Exercise.objects')
    def test_add_exercise_routine_invalid_exercise(self, mock_exercise_objs,
                                                   mock_transaction, mock_api_error):
        request_data = {
            'exercises': [{
                "duration": "00:31:00",
                "id": 221
            },
                {
                    "duration": "03:23:22",
                    "id": 123
                }
            ]
        }
        mock_exercises = []
        for i in range(2):
            mock_exercise = MagicMock()
            mock_exercise.id = i
            mock_exercises.append(mock_exercise)
        mock_exercise_objs.filter.return_value = mock_exercises
        mock_transaction.atomic.return_value = MagicMock()
        mock_api_error.return_value = api_error(f"Exercise with ID 221 not found")
        response = self.factory.add_exercise(request_data)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': 'Exercise with ID 221 not found', 'code': 400}, response.data)
        mock_api_error.assert_called_with("Exercise with ID 221 not found")

    @patch('routines.views.uuid')
    @patch('routines.views.GetExercisesSerializer')
    @patch('routines.views.UserExerciseSerializer')
    @patch('routines.views.FitnessRoutineSerializer')
    @patch('routines.views.transaction')
    @patch('routines.views.api_created_success')
    @patch('routines.views.UserExercise.objects')
    @patch('routines.views.Exercise.objects')
    def test_add_exercise_routine_success(self, mock_exercise_objs, mock_user_exercise_objs,
                                          mock_api_created_success, mock_transaction, mock_routine_serializer,
                                          mock_user_exercise_serializer_obj, mock_get_exercises_serializer,
                                          mock_uuid):
        mock_uuid.uuid4.return_value = MagicMock()
        mock_uuid.uuid4.return_value.hex = 'bf02e92d1ccb4ebbae6da36954f9db20'

        mock_atomic_transaction = MagicMock()
        mock_transaction.atomic.return_value = mock_atomic_transaction

        # filter on exercise
        mock_exercise = MagicMock()
        mock_exercise.key = 'TRICEP01'
        mock_exercise.name = 'Tricep Extension'
        mock_exercise.description = '1. Hold a dumbbell overhead with both hands.\n2. Lower it behind your head by bending your elbows.\n3. Extend your arms back to the starting position.'
        mock_exercise.id = 179
        mock_exercise.category = 'UB'
        mock_exercise_objs.filter.return_value = [mock_exercise]

        # mock UserExercise
        mock_user_exercise = MagicMock()
        mock_user_exercise.id = 123
        mock_user_exercise_objs.create.return_value = mock_user_exercise

        # mocking FitnessRoutineSerializer
        mock_routine_serializer.return_value = MagicMock()
        mock_routine_serializer.return_value.is_valid.return_value = True
        mock_routine_serializer.return_value.save.return_value = None

        # mocking UserExercise
        mock_user_exercise_serializer_obj.return_value = MagicMock()  # might neeed to change this to a dictionary
        mock_user_exercise_serializer_obj.return_value.data = {
            "id": 313,
            "duration": "00:31:00",
            "completed": False,
        }

        fake_exercise = {
            "id": 179,
            "key": "TRICEP01",
            "name": "Tricep Extension",
            "description": "1. Hold a dumbbell overhead with both hands.\n2. Lower it behind your head by bending your elbows.\n3. Extend your arms back to the starting position.",
            "category": "UB"
        }
        mock_get_exercises_serializer.return_value = MagicMock()
        mock_get_exercises_serializer.return_value.data = fake_exercise

        expected_response = {
            "user": 19,
            "exercises": [
                {"id": 313,
                 "duration": "00:31:00",
                 "completed": False,
                 "exercise": fake_exercise
                 }
            ],
            "routine_name": "Small belly with broad shoulder",
            "start_date": "2025-04-20T10:45:56.667726Z",
            "completed": False,
            "routine_id": "bf02e92d1ccb4ebbae6da36954f9db20"
        }

        # mock_request_data = MagicMock()
        # mock_request_data.data.return_value = request_data
        mock_api_created_success.return_value = api_created_success(expected_response)

        mock_req_data = MagicMock()
        mock_req_data.data.return_value = {
            "user": 19,
            'exercises': [{
                "duration": "00:31:00",
                "id": 179
            }
            ],
            "routine_name": "Small belly with broad shoulder",
            "start_date": "2025-04-20T10:45:56.667726Z",
            "completed": False
        }

        response = self.factory.add_exercise(mock_req_data.data.return_value)
        self.assertEqual(201, response.status_code)
        self.assertEqual({'data': expected_response}, response.data)
        mock_api_created_success.assert_called_with(expected_response)

    @patch('routines.views.FitnessRoutine.objects')
    def test_get_object_success(self, mock_fitness_routine_objs):
        pk, routine_id = 10, 21,
        mock_fitness_routine = MagicMock()
        mock_fitness_routine_objs.filter.return_value = mock_fitness_routine
        mock_fitness_routine_by_id = MagicMock()
        mock_fitness_routine_objs.filter.return_value.filter.return_value = mock_fitness_routine_by_id
        FitnessRoutineView().get_object(pk, routine_id)
        mock_fitness_routine_objs.filter.assert_called_with(user=pk)


    @patch('routines.views.FitnessRoutine.objects')
    def test_get_object_raised_exception(self, mock_fitness_routine_objs):
        pk, routine_id = 10, 21
        with self.assertRaises(Http404):
            mock_fitness_routine_objs.filter.side_effect = FitnessRoutine.DoesNotExist
            FitnessRoutineView().get_object(pk, routine_id)


    @patch('routines.views.api_error')
    def test_no_exercise_provided(self, mock_api_error):
        err_msg = "No exercises provided"
        mock_request_data = MagicMock()
        mock_request_data.data = {}
        mock_api_error.return_value = api_error(err_msg)
        response = self.factory.add_exercise(mock_request_data.data)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': err_msg}, response.data)


    @patch('routines.views.UserExercise.objects')
    @patch('routines.views.Exercise.objects')
    @patch('routines.views.transaction')
    @patch('routines.views.FitnessRoutineSerializer')
    @patch('routines.views.api_error')
    def test_invalid_request(self, mock_api_error, mock_routines_serializer, mock_transaction,
                             mock_exercise_objs, mock_user_exercise_objs):
        mock_transaction.atomic.return_value = MagicMock()
        mock_exercise_objs.filter.return_value = MagicMock()

        err_messages = [
            'Invalid request',
        ]

        mock_routines_serializer.return_value = MagicMock()
        mock_routines_serializer.return_value.is_valid.return_value = False
        mock_routines_serializer.return_value.errors = err_messages


        # filter on exercise
        mock_exercise = MagicMock()
        mock_exercise.key = 'TRICEP01'
        mock_exercise.name = 'Tricep Extension'
        mock_exercise.description = '1. Hold a dumbbell overhead with both hands.\n2. Lower it behind your head by bending your elbows.\n3. Extend your arms back to the starting position.'
        mock_exercise.id = 179
        mock_exercise.category = 'UB'
        mock_exercise_objs.filter.return_value = [mock_exercise]

        # mock UserExercise
        mock_user_exercise = MagicMock()
        mock_user_exercise.id = 13
        mock_user_exercise_objs.create.return_value = mock_user_exercise

        mock_api_error.return_value = api_error(err_messages)

        mock_req_data = MagicMock()
        mock_req_data.data.return_value = {
            "user": 19,
            'exercises': [{
                "duration": "00:31:00",
                "id": 179
            }
            ],
            "routine_name": "Small belly with broad shoulder",
            "start_date": "2025-04-20T10:45:56.667726Z",
            "completed": False
        }

        response = self.factory.add_exercise(mock_req_data.data.return_value)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'code': 400, 'message': err_messages}, response.data)
        mock_api_error.assert_called_with(err_messages)



