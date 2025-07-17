from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError

from app import services
from app.models import AttractionSchedule, PointOfInterest

pytestmark = pytest.mark.django_db


def test_create_and_get_poi():
    user = get_user_model().objects.create(username='svcuser', password='pw')
    poi = services.create_poi(
        user, 'Castle', Point(1, 2), translations={'de': {'name': 'Burg', 'description': 'Schön'}}
    )
    assert PointOfInterest.objects.count() == 1
    name, desc = services.get_translation(poi, 'de')
    assert name == 'Burg'
    assert desc == 'Schön'


def test_add_item_and_overlap_detection():
    user = get_user_model().objects.create(username='ituser', password='pw')
    iti = services.create_itinerary(user, 'Summer trip')
    poi = services.create_poi(user, 'Museum', Point(1, 1))
    item1 = services.add_itinerary_item(iti, poi, date.today(), time(10, 0), time(12, 0))
    with pytest.raises(ValidationError):
        services.add_itinerary_item(iti, poi, date.today(), time(11, 0), time(13, 0))


def test_booking_flow():
    user = get_user_model().objects.create(username='bkuser', password='pw')
    poi = services.create_poi(user, 'Zoo', Point(0, 1))
    schedule = AttractionSchedule.objects.create(
        poi=poi, start='2040-01-01T10:00Z', end='2040-01-01T12:00Z', total_capacity=100, remaining_capacity=10
    )
    iti = services.create_itinerary(user, 'Zoo Day')
    item = services.add_itinerary_item(iti, poi, date.today(), time(10, 0), time(12, 0))
    booking = services.create_booking(user, item, schedule, 2)
    schedule.refresh_from_db()
    assert schedule.remaining_capacity == 8
    services.cancel_booking(booking)
    schedule.refresh_from_db()
    assert schedule.remaining_capacity == 10
