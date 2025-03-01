from rest_framework import serializers

from fitness.models import FitnessRecommendation, Recommendation, UserFitness


class FitnessRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessRecommendation
        exclude = ['created_at', 'recommendation']


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class UserFitnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFitness
        fields = '__all__'
