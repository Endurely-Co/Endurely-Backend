import test

import pytest


@pytest.mark.django_db
def test_meal_info(meal_info):
    assert meal_info.id > 0

