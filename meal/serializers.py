from rest_framework import serializers

from meal.models import MealPlan, MealRecommendation, MealInfo


class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = '__all__'


class MealInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealInfo
        fields = '__all__'


class MealRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRecommendation
        fields = '__all__'
