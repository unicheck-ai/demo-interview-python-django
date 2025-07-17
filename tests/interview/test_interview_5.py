import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse

from app.models import PointOfInterest

pytestmark = [pytest.mark.django_db]


@pytest.mark.xfail(strict=True)
def test_delete_poi_should_be_soft(authenticated_api_client, user):
    poi = PointOfInterest.objects.create(operator=user, name='Bridge', location=Point(1.0, 2.0))
    detail_url = reverse('api:pointofinterest-detail', args=[poi.id])

    # Hard delete should be replaced by a soft-delete mechanism
    del_resp = authenticated_api_client.delete(detail_url)
    assert del_resp.status_code in (204, 200)

    # Row must still exist in DB
    assert PointOfInterest.objects.filter(id=poi.id).exists(), 'POI row should remain (soft delete)'

    # But list endpoint must not return soft-deleted record
    list_url = reverse('api:pointofinterest-list')
    list_resp = authenticated_api_client.get(list_url)
    results = list_resp.data['results'] if 'results' in list_resp.data else list_resp.data
    assert all(r['id'] != poi.id for r in results), 'Soft-deleted POIs must be filtered out from default queries'
