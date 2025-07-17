import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from app.models import PointOfInterest

pytestmark = pytest.mark.django_db


def test_schedule_crud(authenticated_api_client, user):
    poi = PointOfInterest.objects.create(operator=user, name='Ferris wheel', location=Point(2, 3))
    url = reverse('api:attractionschedule-list')
    data = {
        'poi': poi.id,
        'start': '2040-06-01T10:00:00Z',
        'end': '2040-06-01T12:00:00Z',
        'total_capacity': 80,
        'remaining_capacity': 80,
        'is_active': True,
    }
    resp = authenticated_api_client.post(url, data, format='json')
    assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
    sid = resp.data['id']
    getresp = authenticated_api_client.get(f'{url}{sid}/')
    assert getresp.data['poi'] == poi.id
    assert getresp.data['total_capacity'] == 80
    patch = authenticated_api_client.patch(f'{url}{sid}/', {'is_active': False}, format='json')
    assert patch.status_code == status.HTTP_200_OK
    deleteresp = authenticated_api_client.delete(f'{url}{sid}/')
    assert deleteresp.status_code in (204, 200, 202)
