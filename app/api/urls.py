from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AttractionScheduleViewSet,
    BookingViewSet,
    HealthCheckView,
    ItineraryItemViewSet,
    ItineraryViewSet,
    POIViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register('pois', POIViewSet)
router.register('schedules', AttractionScheduleViewSet)
router.register('itineraries', ItineraryViewSet)
router.register('itinerary-items', ItineraryItemViewSet)
router.register('bookings', BookingViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]

app_name = 'api'
