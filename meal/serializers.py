from rest_framework import serializers

from meal.models import MealPlan, MealRecommendation, MealInfo

required = {'required': True}

class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = '__all__'


class MealInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealInfo
        fields = '__all__'
        extra_kwargs = {'meal': required, 'calorie': required}


class MealRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRecommendation
        fields = '__all__'
