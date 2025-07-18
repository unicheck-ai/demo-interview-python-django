from django.contrib.gis.geos import Point
from rest_framework import serializers

from app.models import AttractionSchedule, Booking, Itinerary, ItineraryItem, PointOfInterest, POITranslation, Review
from app.services import get_translation


class POITranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = POITranslation
        fields = ['language_code', 'name', 'description']


class PointOfInterestSerializer(serializers.ModelSerializer):
    translations = POITranslationSerializer(many=True, read_only=True)
    location = serializers.JSONField()

    class Meta:
        model = PointOfInterest
        fields = ['id', 'location', 'name', 'operator', 'translations', 'created_at', 'updated_at']
        read_only_fields = ['operator']

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        location = data.get('location')
        if isinstance(location, dict) and location.get('type') == 'Point':
            coords = location.get('coordinates')
            ret['location'] = Point(float(coords[0]), float(coords[1]))
        return ret

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        loc = instance.location
        if isinstance(loc, Point):
            rep['location'] = {'type': 'Point', 'coordinates': [loc.x, loc.y]}
        translation, _ = get_translation(instance)
        rep['name'] = translation
        return rep


class AttractionScheduleSerializer(serializers.ModelSerializer):
    poi = serializers.PrimaryKeyRelatedField(queryset=PointOfInterest.objects.all())

    class Meta:
        model = AttractionSchedule
        fields = ['id', 'poi', 'start', 'end', 'total_capacity', 'remaining_capacity', 'is_active']


class ItineraryItemSerializer(serializers.ModelSerializer):
    poi = PointOfInterestSerializer(read_only=True)
    poi_id = serializers.PrimaryKeyRelatedField(queryset=PointOfInterest.objects.all(), write_only=True, source='poi')

    class Meta:
        model = ItineraryItem
        fields = ['id', 'poi', 'poi_id', 'date', 'start_time', 'end_time', 'order', 'itinerary']
        extra_kwargs = {'itinerary': {'write_only': True}}


class ItinerarySerializer(serializers.ModelSerializer):
    items = ItineraryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Itinerary
        fields = ['id', 'user', 'name', 'items', 'created_at', 'updated_at']
        read_only_fields = ['user']


class BookingSerializer(serializers.ModelSerializer):
    itinerary_item_id = serializers.PrimaryKeyRelatedField(
        queryset=ItineraryItem.objects.all(), source='itinerary_item'
    )
    schedule_id = serializers.PrimaryKeyRelatedField(queryset=AttractionSchedule.objects.all(), source='schedule')

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'itinerary_item_id',
            'schedule_id',
            'seats',
            'status',
            'payment_ref',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['user', 'status', 'payment_ref']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'poi', 'rating', 'text', 'created_at']
        read_only_fields = ['user']
