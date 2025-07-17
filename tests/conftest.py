from typing import Any

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user(db: Any) -> User:
    return User.objects.create_user(username='testuser', password='password123')


@pytest.fixture
def api_client() -> APIClient:
    client = APIClient()
    return client


@pytest.fixture
def authenticated_api_client(user: User, api_client: APIClient) -> APIClient:
    api_client.force_authenticate(user)
    return api_client
