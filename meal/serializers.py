from rest_framework import serializers

from meal.models import MealPlan, MealRecommendation, MealInfo, NutritionInfo, FoodItem

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


class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionInfo
        exclude = ['created_at']


class NutrientSerializer(serializers.Serializer):
    name = serializers.CharField()
    summary = serializers.CharField()


class FoodItemSerializer(serializers.ModelSerializer):
    macronutrients = NutrientSerializer(many=True, required=False)
    vitamins = NutrientSerializer(many=True, required=False)
    minerals = NutrientSerializer(many=True, required=False)

    class Meta:
        model = FoodItem
        fields = ["item", "valid", "macronutrients", "vitamins", "minerals", "other_nutrients", "id"]
