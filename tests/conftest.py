import pytest
from django.contrib.auth import get_user_model

from .utils import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def test_user() -> User:
    return User.objects.create_user(
        username='test-user', email='test-user@example.com', password='password'
    )


@pytest.fixture
def test_user_api_client(api_client, test_user) -> APIClient:
    api_client.login(test_user)
    return api_client
