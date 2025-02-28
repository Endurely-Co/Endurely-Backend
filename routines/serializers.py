from rest_framework import serializers

from routines.models import Exercise, FitnessRoutine,NutritionInfo


class GetExercisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = "__all__"


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['category']


class FitnessRoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessRoutine
        fields = ["user", "exercise", "routine_name", "routine_set", "routine_reps",
                  "routine_duration", "completed", "created_at"]


class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionInfo
        # fields = [
        #     "created_at", "food_name", "user", "nutrient"
        # ]
        exclude = ['created_at']

