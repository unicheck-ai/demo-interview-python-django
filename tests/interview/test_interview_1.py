import math

import pytest
from django.contrib.gis.geos import Point

from app.services import haversine

pytestmark = [pytest.mark.django_db]


@pytest.mark.xfail(strict=True)
def test_haversine_positive_longitude_distance():
    # Approx distance between (0,0) and (1,0) at equator: ~111.319 km
    p1 = Point(0.0, 0.0)
    p2 = Point(1.0, 0.0)
    distance = haversine(p1, p2)
    assert math.isclose(distance, 111.319, rel_tol=1e-3)


@pytest.mark.xfail(strict=True)
def test_haversine_positive_latitude_distance():
    # Approx distance between (0,0) and (0,1) meridian: ~111.319 km
    p1 = Point(0.0, 0.0)
    p2 = Point(0.0, 1.0)
    distance = haversine(p1, p2)
    assert math.isclose(distance, 111.319, rel_tol=1e-3)
