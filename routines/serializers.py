from rest_framework import serializers

from routines.models import Exercise, FitnessRoutine, NutritionInfo, UserExercise


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
                  "routine_duration", "completed", "created_at", "routine_id"]


class UserExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExercise
        exclude = ['created_at', 'image']


class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionInfo
        exclude = ['created_at']
