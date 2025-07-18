import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse

from app.models import Itinerary, ItineraryItem, PointOfInterest

pytestmark = [pytest.mark.django_db]


@pytest.mark.django_db(transaction=True)
def test_itinerary_list_should_not_make_n_plus_one_queries(
    django_assert_max_num_queries, authenticated_api_client, user
):
    # Create sample data: 5 itineraries * 3 items = 15 items
    for i in range(5):
        iti = Itinerary.objects.create(user=user, name=f'Trip {i}')
        for j in range(3):
            poi = PointOfInterest.objects.create(operator=user, name=f'POI {i}-{j}', location=Point(10 + j, 50 + j))
            ItineraryItem.objects.create(
                itinerary=iti,
                poi=poi,
                date='2040-05-20',
                start_time='10:00',
                end_time='11:00',
                order=j,
            )

    url = reverse('api:itinerary-list')
    # Expectation: listing should execute a small, constant number of SQL queries (e.g., <= 6)
    with django_assert_max_num_queries(6):
        response = authenticated_api_client.get(url)
    assert response.status_code == 200
    # Ensure we actually retrieved 5 itineraries
    assert len(response.data['results']) == 5
