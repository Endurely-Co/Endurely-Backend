import pytest


@pytest.mark.django_db
def test_valid_user(project):
    assert project.user.id > 0
