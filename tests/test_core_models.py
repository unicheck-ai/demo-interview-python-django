import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from app.models import PointOfInterest, Review

pytestmark = pytest.mark.django_db


def test_create_poi_with_translation():
    user = get_user_model().objects.create(username='op', password='pw')
    poi = PointOfInterest.objects.create(
        operator=user,
        name='Museum',
        location=Point(2.2945, 48.8584),
    )
    trans = poi.translations.create(language_code='fr', name='Musée', description='Un beau lieu')
    assert PointOfInterest.objects.count() == 1
    assert poi.translations.get(language_code='fr').name == 'Musée'


def test_review_for_poi():
    user = get_user_model().objects.create(username='rv', password='pw')
    poi = PointOfInterest.objects.create(
        operator=user,
        name='Landmark',
        location=Point(0, 0),
    )
    review = Review.objects.create(user=user, poi=poi, rating=4, text='Nice!')
    assert review.rating == 4
    assert str(review).startswith(user.username)
