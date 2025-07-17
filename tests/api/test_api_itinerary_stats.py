from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from app.models import Itinerary, ItineraryItem, PointOfInterest

pytestmark = pytest.mark.django_db


def test_itinerary_stats_endpoint(authenticated_api_client):
    user = get_user_model().objects.create(username='statuser', password='pw')
    iti = Itinerary.objects.create(user=user, name='Stats Test')
    locs = [Point(12.0, 51.0), Point(12.01, 51.005), Point(12.02, 51.01)]
    for i, pt in enumerate(locs):
        poi = PointOfInterest.objects.create(operator=user, name=f'Pt{i}', location=pt)
        ItineraryItem.objects.create(
            itinerary=iti,
            poi=poi,
            date=date(2040, 5, 20),
            start_time=time(10 + i, 0),
            end_time=time(11 + i, 0),
            order=i,
        )
    url = reverse('api:itinerary-stats', args=[iti.id])
    resp = authenticated_api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert 'total_walk_km' in resp.data
    assert 'daily_occupancy' in resp.data
    assert isinstance(resp.data['total_walk_km'], float)
    assert resp.data['daily_occupancy']
