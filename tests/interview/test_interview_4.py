import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse

from app.models import PointOfInterest, POITranslation

pytestmark = [pytest.mark.django_db]


def test_poi_detail_returns_localised_name(authenticated_api_client, user):
    poi = PointOfInterest.objects.create(operator=user, name='Castle', location=Point(10.0, 50.0))
    POITranslation.objects.create(poi=poi, language_code='de', name='Burg', description='Schönes Schloss')

    url = reverse('api:pointofinterest-detail', args=[poi.id])
    resp = authenticated_api_client.get(url, HTTP_ACCEPT_LANGUAGE='de')
    assert resp.status_code == 200
    assert resp.data['name'] == 'Burg'
