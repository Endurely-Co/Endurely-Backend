from rest_framework import serializers

from routines.models import Exercise, FitnessRoutine, UserExercise


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
        fields = ["user", "exercise", "routine_name",
                  "completed", "start_date",
                  "created_at", "routine_id"]


class UserExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExercise
        exclude = ['created_at', 'image']
