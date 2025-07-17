from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db import models
from django.utils.translation import gettext_lazy as _


class PointOfInterestQuerySet(gis_models.QuerySet):
    def with_avg_rating(self):
        return self.annotate(avg_rating=models.Avg('reviews__rating'))

    def within_radius(self, point, radius_km):
        return self.filter(location__distance_lte=(point, D(km=radius_km))).annotate(
            distance=Distance('location', point)
        )

    def order_by_distance(self, point):
        return self.annotate(distance=Distance('location', point)).order_by('distance')


class PointOfInterest(gis_models.Model):
    location = gis_models.PointField(geography=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pois')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PointOfInterestQuerySet.as_manager()

    class Meta:
        verbose_name = _('Point of Interest')
        verbose_name_plural = _('Points of Interest')
        ordering = ['id']

    def __str__(self):
        return self.name


class POITranslation(models.Model):
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE, related_name='translations')
    language_code = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('poi', 'language_code')
        verbose_name = _('POI Translation')
        verbose_name_plural = _('POI Translations')


class AttractionSchedule(models.Model):
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE, related_name='schedules')
    start = models.DateTimeField()
    end = models.DateTimeField()
    total_capacity = models.PositiveIntegerField()
    remaining_capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Attraction Schedule')
        verbose_name_plural = _('Attraction Schedules')
        ordering = ['start']

    def __str__(self):
        return f'{self.poi.name} {self.start} - {self.end}'


class Itinerary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='itineraries')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Itinerary')
        verbose_name_plural = _('Itineraries')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user.username})'


class ItineraryItem(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='items')
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Itinerary Item')
        verbose_name_plural = _('Itinerary Items')
        ordering = ['date', 'order']
        unique_together = (('itinerary', 'date', 'order'),)


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    itinerary_item = models.ForeignKey(ItineraryItem, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey(AttractionSchedule, on_delete=models.CASCADE, related_name='bookings')
    seats = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_ref = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} booking {self.status}'


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = (('user', 'poi'),)

    def __str__(self):
        return f'{self.user.username} review for {self.poi.name}'
