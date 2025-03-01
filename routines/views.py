from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from utils.api import api_success, api_error, api_created_success
from utils.gemini import GeminiApi

from .models import Exercise, FitnessRoutine
from .serializers import GetExercisesSerializer, FitnessRoutineSerializer, NutritionSerializer


class AuthenticatedAPIView(APIView):
    permission_classes = [permissions.AllowAny]  # Change to Authenticated later on


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

    def get_object(self, pk):
        try:
            return FitnessRoutine.objects.get(pk=pk)
        except FitnessRoutine.DoesNotExist:
            raise Http404

    def post(self, request):
        routine_serializer = FitnessRoutineSerializer(data=request.data)
        if routine_serializer.is_valid():
            routine_serializer.save()
            return api_created_success(routine_serializer.data)
        return api_error(routine_serializer.errors)

    def get(self, _, pk=''):
        if len(pk) > 0 and pk.isnumeric():
            snippet = self.get_object(pk)
            serializer = FitnessRoutineSerializer(snippet)
        elif len(pk) == 0:
            snippet = FitnessRoutine.objects.all()
            serializer = FitnessRoutineSerializer(snippet, many=True)
        else:
            return api_error("url requires an id")
        return api_created_success(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = FitnessRoutineSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_success(serializer.data)
        return api_error(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
