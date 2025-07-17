import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_health_check(api_client):
    url = reverse('api:health-check')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
