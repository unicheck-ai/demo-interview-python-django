import pytest
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from app.models import PointOfInterest, Review

pytestmark = [pytest.mark.django_db]


def test_duplicate_review_updates_not_crashes():
    user = User.objects.create_user(username='dup', password='pw')
    client = APIClient()
    client.force_authenticate(user)
    poi = PointOfInterest.objects.create(operator=user, name='Waterfall', location=Point(10.0, 50.0))

    first_resp = client.post('/api/reviews/', {'poi': poi.id, 'rating': 3, 'text': 'Ok'}, format='json')
    assert first_resp.status_code == 201
    assert Review.objects.count() == 1

    second_resp = client.post('/api/reviews/', {'poi': poi.id, 'rating': 5, 'text': 'Great'}, format='json')
    # Expected behaviour: existing review updated, no server error, still single review row
    assert second_resp.status_code == 200
    assert Review.objects.count() == 1
    review = Review.objects.first()
    assert review.rating == 5
