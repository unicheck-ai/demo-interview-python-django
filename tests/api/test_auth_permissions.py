import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from app.models import Itinerary, PointOfInterest

pytestmark = pytest.mark.django_db


def test_itinerary_permissions(api_client, user):
    other_user = get_user_model().objects.create(username='other', password='pw')
    iti = Itinerary.objects.create(user=user, name='Test I')
    url = reverse('api:itinerary-detail', args=[iti.id])
    update_resp = api_client.patch(url, {'name': 'Update'}, format='json')
    assert update_resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_itinerary_forbidden(authenticated_api_client, user):
    other = get_user_model().objects.create(username='forbid', password='pw2')
    iti = Itinerary.objects.create(user=other, name='Not Yours')
    url = reverse('api:itinerary-detail', args=[iti.id])
    resp = authenticated_api_client.patch(url, {'name': 'Nono'}, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_poi_operator_permissions(authenticated_api_client, user):
    other = get_user_model().objects.create(username='op', password='pw')
    poi = PointOfInterest.objects.create(operator=other, name='Big Place', location=Point(11.11, 51.12))
    url = reverse('api:pointofinterest-detail', args=[poi.id])
    resp = authenticated_api_client.patch(url, {'name': 'New Name'}, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN
