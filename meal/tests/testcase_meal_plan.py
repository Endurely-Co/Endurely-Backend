import unittest
from unittest.mock import patch, MagicMock

from meal.tests.factory.meal_plan_factory import MealPlanFactory


class MealPlanViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = MealPlanFactory()

    @patch('meal.views.FoodItemSerializer')
    @patch('meal.views.MealPlanSerializer')
    @patch('meal.views.MealPlan.objects')
    def test_get_meal_plans_failed(self, mock_meal_plan_objs, mock_mp_serializer_class, mock_fi_serializer_class):
        user_id, meal_plan_id = 2, '1'
        mock_meal_plan_qs = MagicMock()
        mock_user_by_id_qs = MagicMock()

        mock_meal_plan_objs.filter(user=user_id).return_value = mock_user_by_id_qs
        mock_meal_plan_objs.filter.return_value.filter(meal_plan_id=meal_plan_id).return_value = mock_meal_plan_qs

        response = self.factory.get_plan_by_id(user_id=user_id, plan_id=meal_plan_id)
        mock_meal_plan_objs.filter.assert_called_with(user=user_id)

        # check meal plan
        mock_meal_plan_objs.filter(user=user_id).filter.assert_called_with(meal_plan_id=meal_plan_id)




    def test_delete_meal_plan(self):
        pass

    def test_post_meal_plan(self):
        pass


    def doCleanups(self):
        self.factory.tear_down()
