from pydantic import ValidationError
import uuid
from datetime import timedelta

from django.db import transaction
from django.http import Http404

from utils.api import api_success, api_error, api_created_success
from utils.api_ext import AuthenticatedAPIView
from utils.validator import check_none
from .models import Exercise, FitnessRoutine, UserExercise
from .serializers import GetExercisesSerializer, FitnessRoutineSerializer, UserExerciseSerializer


class GetExercises(AuthenticatedAPIView):
    """
    API view to retrieve all exercises.
    """

    def get(self, _):
        """
        Retrieves all exercises from the database, ordered by category.

        Returns:
            Response: An api_success response containing serialized exercise data.
        """
        try:
            exercises = Exercise.objects.all().order_by('category')
            serializer = GetExercisesSerializer(exercises, many=True)
            return api_success(serializer.data)
        except Exception:
            return api_error('Invalid server error')


class FitnessRoutineView(AuthenticatedAPIView):
    """
    API view to handle fitness routine operations (create, retrieve, update, delete).
    """

    def get_object(self, pk, routine_id=None):
        """
        Retrieves FitnessRoutine objects based on user ID and optionally a routine ID.

        Args:
            pk (int): User ID.
            routine_id (str, optional): Routine ID. Defaults to None.

        Returns:
            QuerySet: A queryset of FitnessRoutine objects.

        Raises:
            Http404: If no FitnessRoutine is found for the given criteria.
        """
        try:
            fitness_routine = FitnessRoutine.objects.filter(user=pk)
            return fitness_routine.filter(routine_id=routine_id) if routine_id else fitness_routine
        except FitnessRoutine.DoesNotExist:
            raise Http404

    def post(self, request):
        """
        Creates a new fitness routine.

        Args:
            request (HttpRequest): The HTTP request object. The request data should contain
                a list of exercises with their IDs and durations.

        Returns:
            Response: An api_created_success response containing the created routine data.
        """

        try:
            exercises_data = request.data.get('exercises', [])
            request.data['routine_id'] = uuid.uuid4().hex  # Generate a unique routine ID

            if not exercises_data:
                return api_error("No exercises provided")

            exercise_ids = [exercise_obj['id'] for exercise_obj in exercises_data]

            # Bulk fetch all exercises to avoid N+1 queries
            exercise_map = {exercise.id: exercise for exercise in Exercise.objects.filter(id__in=exercise_ids)}

            exercises = []

            with transaction.atomic():  # Ensures all DB operations are atomic
                for exercise_obj in exercises_data:
                    exercise = exercise_map.get(exercise_obj['id'])
                    if not exercise:
                        return api_error(f"Exercise with ID {exercise_obj['id']} not found")

                    hours, minutes, seconds = map(int, exercise_obj['duration'].split(":"))
                    user_exercise = UserExercise.objects.create(
                        exercise=exercise,
                        duration=timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    )

                    request.data['exercise'] = user_exercise.id
                    routine_serializer = FitnessRoutineSerializer(data=request.data)

                    if routine_serializer.is_valid():
                        routine_serializer.save()
                        user_exercise_serializer = UserExerciseSerializer(user_exercise).data
                        user_exercise_serializer['exercise'] = GetExercisesSerializer(exercise).data
                        exercises.append(user_exercise_serializer)
                    else:
                        return api_error(routine_serializer.errors)

            request.data.pop('exercise')
            request.data['exercises'] = exercises

            return api_created_success(request.data)
        except (ValidationError, Http404) as e:
            return api_error('Internal server error')

    def get(self, request, pk=0):
        """
        Retrieves fitness routines for a given user, optionally filtered by routine ID.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): User ID.
            routine_id (str, optional): Routine ID. Defaults to None.

        Returns:
            Response: An api_success response containing the serialized routine data.
        """

        routine_param = request.query_params.get('routine')
        routine_id = routine_param if routine_param else None

        if type(pk) is not int:
            return api_error(f"{pk} not a valid type")

        if pk <= 0:
            return api_error("invalid user id")

        routines = self.get_object(pk=pk, routine_id=routine_id)

        serializer_data = FitnessRoutineSerializer(routines, many=True).data

        in_response = {}
        distinct_exercises = {}

        exercise_ids = {serializer['exercise'] for serializer in serializer_data}
        user_exercises = {ue.pk: ue for ue in UserExercise.objects.filter(pk__in=exercise_ids)}
        exercise_map = {e.id: e for e in
                        Exercise.objects.filter(id__in=[ue.exercise.id for ue in user_exercises.values()])}

        for serializer in serializer_data:
            user_exercise = user_exercises.get(serializer['exercise'])

            if not user_exercise:
                continue  # Skip if user_exercise doesn't exist

            exercises = [exercise_map.get(user_exercise.exercise.id)]
            exercises_serializer = GetExercisesSerializer(exercises, many=True).data

            user_exercises_serializer = UserExerciseSerializer(user_exercise).data
            user_exercises_serializer['exercise'] = exercises_serializer[0]

            routine_id = serializer['routine_id']

            if routine_id in distinct_exercises:
                distinct_exercises[routine_id].append(user_exercises_serializer)
            else:
                distinct_exercises[routine_id] = [user_exercises_serializer]
                serializer['exercises'] = distinct_exercises[routine_id]
                in_response[routine_id] = serializer

            serializer.pop('exercise')

        return api_success(in_response.values())

    @transaction.atomic()
    def put(self, request, pk, format=None):
        """
        Updates an existing fitness routine.

        Args:
            request (HttpRequest): The HTTP request object. The request data should contain
                the updated routine information, including exercises and their durations.
            pk (int): The user ID.
            format (str, optional): The request format. Defaults to None.

        Returns:
            Response: An api_success response containing the updated routine data.

        Raises:
            UserExercise.DoesNotExist: If a UserExercise with the given ID does not exist.
            Exercise.DoesNotExist: If an Exercise with the given ID does not exist.
            KeyError: If a required key is missing from the request data.
        """
        try:
            exercise_list, existing_routine_data = [], {}

            exercises = request.data['exercises']

            existing_routine = None
            del_routine = FitnessRoutine.objects.filter(user=pk) \
                .filter(routine_id=request.data['routine_id'])

            if not del_routine.exists():
                return api_error("Record does not exist")

            mod_routine = del_routine[0]
            del_routine.delete()

            for exercise in exercises:
                ex_key = exercise.get('user_exercise_id')
                exercise_obj = Exercise.objects.get(id=exercise['id'])
                hours, minutes, seconds = map(int, exercise['duration'].split(":"))
                user_exercise, created = UserExercise.objects.update_or_create(
                    id=exercise.get('user_exercise_id'),  # The lookup field (determines existence)
                    defaults={"duration": timedelta(minutes=minutes, seconds=seconds, hours=hours),
                              "exercise": exercise_obj, "completed": exercise["completed"]}
                    # Fields to update if found, or set if created
                )

                existing_routine, created = FitnessRoutine.objects.update_or_create(
                    user=mod_routine.user,
                    exercise=user_exercise,
                    defaults={
                        "start_date": request.data.get("meal_date_time"),
                        "routine_name": check_none(request.data.get("routine_name"), mod_routine.routine_name),
                        "routine_id": mod_routine.routine_id,
                        "completed": check_none(request.data.get("completed"), mod_routine.completed),
                    }
                )

                exercise_list.append(UserExerciseSerializer(user_exercise).data)

            existing_routine_data = FitnessRoutineSerializer(existing_routine).data
            existing_routine_data['exercises'] = exercise_list
            return api_success(existing_routine_data)
        except (UserExercise.DoesNotExist, Exercise.DoesNotExist, KeyError) as e:
            return api_error(f"{e}")

    def delete(self, request, pk):
        """
        Deletes a fitness routine.

        Args:
            request (HttpRequest): The HTTP request object.
            pk (int): The user ID.

        Returns:
            Response: An api_success response indicating the routine was deleted.
        """
        routine_param = request.query_params.get('routine')
        if type(routine_param) is not str:
            return api_error(f"{routine_param} not a valid type")
        snippet = self.get_object(pk, routine_param)

        if len(snippet) <= 0:
            return api_success(f"No routine matching this id: {routine_param}")
        snippet.delete()
        return api_success("Routine was deleted.")
