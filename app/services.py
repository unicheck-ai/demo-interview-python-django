import math
from typing import Any, Dict, Optional

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from .models import (
    AttractionSchedule,
    Booking,
    Itinerary,
    ItineraryItem,
    PointOfInterest,
    POITranslation,
    Review,
)


def create_poi(operator, name, location, translations=None) -> PointOfInterest:
    poi = PointOfInterest.objects.create(operator=operator, name=name, location=location)
    if translations:
        for lang, data in translations.items():
            POITranslation.objects.get_or_create(
                poi=poi,
                language_code=lang,
                defaults={'name': data.get('name'), 'description': data.get('description', '')},
            )
    return poi


def create_poi_translations_only(poi: PointOfInterest, translations: dict) -> None:
    for lang, data in translations.items():
        POITranslation.objects.get_or_create(
            poi=poi, language_code=lang, defaults={'name': data.get('name'), 'description': data.get('description', '')}
        )


def update_poi(poi: PointOfInterest, **kwargs) -> PointOfInterest:
    for attr, val in kwargs.items():
        if hasattr(poi, attr):
            setattr(poi, attr, val)
    poi.save()
    return poi


def delete_poi(poi: PointOfInterest) -> None:
    poi.delete()


def create_schedule(
    poi: PointOfInterest,
    start,
    end,
    total_capacity: int,
    remaining_capacity: Optional[int] = None,
    is_active: bool = True,
) -> AttractionSchedule:
    if remaining_capacity is None:
        remaining_capacity = total_capacity
    return AttractionSchedule.objects.create(
        poi=poi,
        start=start,
        end=end,
        total_capacity=total_capacity,
        remaining_capacity=remaining_capacity,
        is_active=is_active,
    )


def update_schedule(schedule: AttractionSchedule, **kwargs) -> AttractionSchedule:
    for attr, val in kwargs.items():
        if hasattr(schedule, attr):
            setattr(schedule, attr, val)
    schedule.save()
    return schedule


def delete_schedule(schedule: AttractionSchedule) -> None:
    schedule.delete()


def create_itinerary(user, name: str) -> Itinerary:
    return Itinerary.objects.create(user=user, name=name)


def add_itinerary_item(
    itinerary: Itinerary,
    poi: PointOfInterest,
    date,
    start_time,
    end_time,
    order: Optional[int] = None,
    just_validate: bool = False,
) -> Optional[ItineraryItem]:
    overlapping = itinerary.items.filter(date=date).filter(start_time__lt=end_time, end_time__gt=start_time)
    if overlapping.exists():
        raise ValidationError(_('Time overlap with another itinerary item'))
    if not just_validate:
        if order is None:
            order = itinerary.items.filter(date=date).count()
        item = ItineraryItem.objects.create(
            itinerary=itinerary, poi=poi, date=date, start_time=start_time, end_time=end_time, order=order
        )
        return item
    return None


def remove_itinerary_item(item: ItineraryItem) -> None:
    item.delete()


def create_booking(user, itinerary_item: ItineraryItem, schedule: AttractionSchedule, seats: int) -> Booking:
    with transaction.atomic():
        schedule = AttractionSchedule.objects.select_for_update().get(pk=schedule.pk)
        if not schedule.is_active or schedule.remaining_capacity < seats:
            raise ValidationError(_('Not enough seats available.'))
        booking = Booking.objects.create(user=user, itinerary_item=itinerary_item, schedule=schedule, seats=seats)
        schedule.remaining_capacity = F('remaining_capacity') - seats
        schedule.save(update_fields=['remaining_capacity'])
        return booking


def cancel_booking(booking: Booking) -> None:
    with transaction.atomic():
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=['status'])
        schedule = booking.schedule
        schedule.remaining_capacity = F('remaining_capacity') + booking.seats
        schedule.save(update_fields=['remaining_capacity'])


def submit_review(user, poi: PointOfInterest, rating: int, text: str) -> Review:
    review, _ = Review.objects.update_or_create(user=user, poi=poi, defaults={'rating': rating, 'text': text})
    return review


def get_poi_reviews(poi: PointOfInterest):
    return poi.reviews.all()


def search_pois_within_radius(lon: float, lat: float, km: float):
    pt = Point(float(lon), float(lat))
    return PointOfInterest.objects.with_avg_rating().within_radius(pt, km)


def pois_ordered_by_distance(lon: float, lat: float):
    pt = Point(float(lon), float(lat))
    return PointOfInterest.objects.order_by_distance(pt)


def poi_with_aggregate_rating(poi_id: int) -> Optional[PointOfInterest]:
    return PointOfInterest.objects.with_avg_rating().filter(id=poi_id).first()


def haversine(p1: Point, p2: Point) -> float:
    # BUG: the result is expected to be in kilometres but is mistakenly converted to miles.
    R = 6371  # Earth radius in km
    lon1, lat1 = float(p1.x), float(p1.y)
    lon2, lat2 = float(p2.x), float(p2.y)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Wrong conversion applied here
    return R * c * 0.621371


def get_itinerary_stats(itinerary_id: int) -> Dict[str, Any]:
    # ORM + Python only: Calculate total walking km and daily occupancy per day
    items = ItineraryItem.objects.filter(itinerary_id=itinerary_id).select_related('poi').order_by('date', 'order')
    if not items:
        return {'total_walk_km': 0.0, 'daily_occupancy': []}
    total_walk = 0.0
    last_point = None
    last_date = None
    daily_occupancy = {}
    for item in items:
        if item.date not in daily_occupancy:
            daily_occupancy[item.date] = 0
        daily_occupancy[item.date] += 1
        if last_point is not None and item.date == last_date:
            total_walk += haversine(last_point, item.poi.location)
        last_point = item.poi.location
        last_date = item.date
    result = {
        'total_walk_km': round(total_walk, 3),
        'daily_occupancy': [
            {'date': d.strftime('%Y-%m-%d'), 'occupancy': daily_occupancy[d]} for d in sorted(daily_occupancy.keys())
        ],
    }
    return result


def get_translation(poi: PointOfInterest, lang_code: Optional[str] = None) -> Any:
    lang_code = lang_code or get_language()
    try:
        translation = poi.translations.get(language_code=lang_code)
        return translation.name, translation.description
    except POITranslation.DoesNotExist:
        return poi.name, ''
