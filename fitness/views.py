from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render

from fitness.models import FitnessRecommendation, Recommendation, UserFitness
from utils.api import api_success, api_created_success, api_error
from utils.api_ext import AuthenticatedAPIView
from utils.gemini import GeminiApi

from fitness.serializers import FitnessRecommendationSerializer, RecommendationSerializer, UserFitnessSerializer


# Create your views here.

class FitnessGoals(AuthenticatedAPIView):
    def get(self, _):
        goals = []
        for goal in UserFitness.FITNESS_GOALS:
            goals.append({
                "key": goal[0],
                "name": goal[1]
            })
        return api_success(goals)

    def post(self, request, *args, **kwargs):
        pass


class FitnessRecommendationView(AuthenticatedAPIView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gemini = GeminiApi()

    """
       def get_object(self, pk):
        try:
            return FitnessRoutine.objects.get(pk=pk)
        except FitnessRoutine.DoesNotExist:
            raise Http404
    """

    def get(self, request, username):
        user = User.objects.get_by_natural_key(username=username)
        if user:
            self.gemini.fitness_recommendation()
            serializer = FitnessRecommendationSerializer()
        pass

    # userid, height,sex, fitness_goal
    def post(self, request, *args, **kwargs):
        request_data = request.data

        # Ask if the user have fitness profile
        try:
            user_fitness = None
            user = User.objects.get(pk=request_data.get('user'))
            user_fitness = UserFitness.objects.get(pk=request_data.get('user'))

            # try:
            #     user_fitness = UserFitness.objects.get(pk=request_data.get('user'))
            # except UserFitness.DoesNotExist as dne:
            #     user_fitness = UserFitness(user=user,
            #                                height=request_data.get('height'),
            #                                sex=request_data.get('sex'),
            #                                fitness_goal=request_data.get('fitness_goal'), )
            #     user_fitness.save()

            result_dict = self.gemini.fitness_recommendation(
                height=user_fitness.height,
                sex=user_fitness.sex,
                fitness_goal=user_fitness.fitness_goal
            )
            print(result_dict, type(result_dict))

            results = result_dict["recommendations"]
            request_data["recommendations"] = []

            fitness_recom = FitnessRecommendation(user=user,
                                                  user_fitness=user_fitness)
            for result in results:
                recom = Recommendation(exercise=result['exercise'],
                                       description=result['description'],
                                       frequency=result['frequency'],
                                       justification=result['justification'])
                recom.save()
                fitness_recom.recommendation = recom
                fitness_recom.save()
                recom_serializer = RecommendationSerializer(recom)
                request_data["recommendations"].append(recom_serializer.data)
            return api_created_success(request_data)
        except IntegrityError as uno:
            return api_error("Oops! Something seems off with your input. Please check and enter a valid value")


class FitnessUserView(AuthenticatedAPIView):

    def post(self, request, *args, **kwargs):
        request_data = request.data
        user = User.objects.get(pk=request_data.get('user'))
        user_fitness = UserFitness(user=user,
                                   height=request_data.get('height'),
                                   sex=request_data.get('sex'),
                                   fitness_goal=request_data.get('fitness_goal'), )
        user_fitness.save()

    def get(self, _, user_id: int):
        if type(user_id) is int:
            user_fitness = UserFitness.objects.get(pk=user_id)
            serializer = UserFitnessSerializer(user_fitness)
            return api_success(serializer.data)
        return api_error("Invalid user")
