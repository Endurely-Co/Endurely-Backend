import uuid
from datetime import timedelta
from threading import Thread

from django.db import transaction
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from utils.api import api_success, api_error, api_created_success
from utils.api_ext import AuthenticatedAPIView
from utils.gemini import GeminiApi

from .models import Exercise, FitnessRoutine, UserExercise
from .serializers import GetExercisesSerializer, FitnessRoutineSerializer, NutritionSerializer, UserExerciseSerializer


# Create your views here.
class GetExercises(AuthenticatedAPIView):

    def get(self, _):
        snippets = Exercise.objects.all().order_by('category')
        serializer = GetExercisesSerializer(snippets, many=True)
        return api_success(serializer.data)


class GetExercisesByCategory(AuthenticatedAPIView):

    def get(self, _, category):
        if len(category) > 2 or not str(category).isalpha():
            return api_error('Wrong category id')
        snippets = Exercise.objects.all().filter(category=category)
        serializer = GetExercisesSerializer(snippets, many=True)
        return api_success(serializer.data)


class GetCategories(AuthenticatedAPIView):

    def get(self, _):
        snippets = Exercise.objects.all().order_by('category')
        response_array = {}
        for i in range(len(snippets)):
            response_array[snippets[i].category] = {
                "category": snippets[i].category,
                "category_name": snippets[i].get_category_display()
            }
        return api_success(response_array.values())


class FitnessRoutineView(AuthenticatedAPIView):

    def get_object(self, pk, routine_id=None):
        try:
            fitness_routine = FitnessRoutine.objects.filter(user=pk)
            return fitness_routine.filter(routine_id=routine_id) if routine_id else fitness_routine
        except FitnessRoutine.DoesNotExist:
            raise Http404

    def post(self, request):
        exercises_data = request.data.get('exercises', [])
        request.data['routine_id'] = uuid.uuid4().hex

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

    def get(self, request, pk=0, ):

        routine_param = request.query_params.get('routine')
        routine_id = routine_param if routine_param else None

        print("id_id", pk, type(routine_param) is not str)

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
            print('serializer_data', serializer['exercise'])
            user_exercise = user_exercises.get(serializer['exercise'])

            if not user_exercise:
                continue  # Skip if user_exercise doesn't exist

            exercises = [exercise_map.get(user_exercise.exercise.id)]
            exercises_serializer = GetExercisesSerializer(exercises, many=True).data

            user_exercises_serializer = UserExerciseSerializer(user_exercise).data
            user_exercises_serializer['exercise'] = exercises_serializer[0]

            routine_id = serializer['routine_id']
            # print("attri", exercises_serializer)

            if routine_id in distinct_exercises:
                distinct_exercises[routine_id].append(user_exercises_serializer)
            else:
                distinct_exercises[routine_id] = [user_exercises_serializer]
                serializer['exercises'] = distinct_exercises[routine_id]
                in_response[routine_id] = serializer

            print("in_response", serializer)
            serializer.pop('exercise')

        # print("in_response", in_response)
        return api_success(in_response.values())

    @transaction.atomic()
    def put(self, request, pk, format=None):
        try:
            exercise_list, existing_routine_data = [], {}

            exercises = request.data['exercises']

            # thread = Thread(target=)
            # thread.start()
            existing_routine = None
            del_routine = FitnessRoutine.objects.filter(user=pk) \
                .filter(routine_id=request.data['routine_id'])

            if not del_routine.exists():
                return api_error("Record does not exist")

            mod_routine = del_routine[0]
            del_routine.delete()

            for exercise in exercises:
                ex_key = exercise.get('user_exercise_id')
                if ex_key:
                    print("exercise", ex_key)
                    exercise_obj = Exercise.objects.get(id=exercise['id'])
                    hours, minutes, seconds = map(int, exercise['duration'].split(":"))
                    user_exercise, created = UserExercise.objects.update_or_create(
                        id=ex_key,  # The lookup field (determines existence)
                        defaults={"duration": timedelta(minutes=minutes, seconds=seconds, hours=hours),
                                  "exercise": exercise_obj, "completed": exercise["completed"]}  # Fields to update if found, or set if created
                    )

                    existing_routine = FitnessRoutine(user=mod_routine.user,
                                                      routine_name=mod_routine.routine_name,
                                                      routine_set=mod_routine.routine_set,
                                                      routine_reps=mod_routine.routine_reps,
                                                      routine_id=mod_routine.routine_id,
                                                      routine_duration=mod_routine.routine_duration,
                                                      completed=mod_routine.completed,
                                                      exercise=user_exercise)
                    existing_routine.save()
                    print("existing_routine", existing_routine)
                    exercise_list.append(UserExerciseSerializer(user_exercise).data)

            existing_routine_data = FitnessRoutineSerializer(existing_routine).data
            existing_routine_data['exercises'] = exercise_list
            return api_success(existing_routine_data)
        except (UserExercise.DoesNotExist, Exercise.DoesNotExist, KeyError) as e:
            return api_error(f"{e}")

    def delete(self, request, pk):
        routine_param = request.query_params.get('routine')
        if type(routine_param) is not str:
            return api_error(f"{routine_param} not a valid type")
        snippet = self.get_object(pk, routine_param)

        if len(snippet) <= 0:
            return api_success(f"No routine matching this id: {routine_param}")
        snippet.delete()
        return api_success("Routine was deleted.")


# 23cf0668153e4d18a4a4bc3ab0f7a0f9

class NutritionView(AuthenticatedAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = GeminiApi()

    def post(self, request):
        food = request.data.get('food_name')
        if food and len(food) > 2:
            response = request.data
            response["nutrient"] = self.gemini.nutrients_from_food(food)
            serializer = NutritionSerializer(data=response)

            if serializer.is_valid():
                print('nutrient', response)
                serializer.save()
                return api_success(response)
            else:
                return api_error("Sorry, you can't use this service at the moment.")
        else:
            return api_error("Food/drink is invalid. Try again!")
