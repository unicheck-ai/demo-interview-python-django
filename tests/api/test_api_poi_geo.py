import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from app.models import PointOfInterest

pytestmark = pytest.mark.django_db


def test_nearby_api(authenticated_api_client):
    user = get_user_model().objects.create(username='geo', password='pw')
    # Add two POIs within ~2km of eachother
    p1 = PointOfInterest.objects.create(operator=user, name='Alpha', location=Point(12.00, 51.00))
    p2 = PointOfInterest.objects.create(operator=user, name='Bravo', location=Point(12.01, 51.00))
    url = reverse('api:pointofinterest-nearby')
    resp = authenticated_api_client.get(url + '?lon=12.00&lat=51.00&radius=3.0')
    assert resp.status_code == status.HTTP_200_OK
    names = [poi['name'] for poi in resp.data['results']]
    assert 'Alpha' in names and 'Bravo' in names


def test_aggregate_rating_api(authenticated_api_client):
    user = get_user_model().objects.create(username='geo2', password='pw')
    poi = PointOfInterest.objects.create(operator=user, name='Rated', location=Point(8, 8))
    # Add reviews manually
    from app.models import Review

    Review.objects.create(user=user, poi=poi, rating=5, text='Great!')
    url = reverse('api:pointofinterest-aggregate', args=[poi.id])
    resp = authenticated_api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['avg_rating'] == 5
