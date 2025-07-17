import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from app.models import PointOfInterest

pytestmark = pytest.mark.django_db


def test_poi_crud(authenticated_api_client):
    url = reverse('api:pointofinterest-list')
    resp = authenticated_api_client.post(
        url,
        {
            'name': 'Place',
            'location': {'type': 'Point', 'coordinates': [12.0, 51.0]},
            'translations': {'fr': {'name': 'Lieu', 'description': 'Desc'}},
        },
        format='json',
    )
    assert resp.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)
    list_resp = authenticated_api_client.get(url)
    assert list_resp.status_code == status.HTTP_200_OK
    results = list_resp.data['results'] if 'results' in list_resp.data else list_resp.data
    assert any(poi['name'] == 'Place' for poi in results)


def test_cannot_create_itinerary_item_overlap(authenticated_api_client):
    User = get_user_model()
    user = User.objects.first() or User.objects.create_user(username='overlap', password='pw123')
    iti_url = reverse('api:itinerary-list')
    iti_resp = authenticated_api_client.post(iti_url, {'name': 'Trip'}, format='json')
    iti_id = iti_resp.data['id']
    poi = PointOfInterest.objects.create(operator=user, name='TestP', location=Point(1, 2))
    item_url = reverse('api:itineraryitem-list')
    data1 = {'itinerary': iti_id, 'poi_id': poi.id, 'date': '2040-01-01', 'start_time': '10:00', 'end_time': '11:00'}
    r1 = authenticated_api_client.post(item_url, data1, format='json')
    assert r1.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
    data2 = {'itinerary': iti_id, 'poi_id': poi.id, 'date': '2040-01-01', 'start_time': '10:30', 'end_time': '11:30'}
    r2 = authenticated_api_client.post(item_url, data2, format='json')
    assert r2.status_code == status.HTTP_400_BAD_REQUEST
