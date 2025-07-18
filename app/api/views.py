from functools import wraps
from typing import Any

from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError, connection
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app import services
from app.models import (
    AttractionSchedule,
    Booking,
    Itinerary,
    ItineraryItem,
    PointOfInterest,
    Review,
)

from .permissions import IsOperatorOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    AttractionScheduleSerializer,
    BookingSerializer,
    ItineraryItemSerializer,
    ItinerarySerializer,
    PointOfInterestSerializer,
    ReviewSerializer,
)


def cache_response(timeout=60):
    # Simple decorator for GET viewmethods with user-unaware cache
    def decorator(view_method):
        @wraps(view_method)
        def _wrapped_view(self, request, *args, **kwargs):
            if request.method != 'GET':
                return view_method(self, request, *args, **kwargs)
            cache_key = f'{self.__class__.__name__}:{view_method.__name__}:{request.get_full_path()}'
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)
            response = view_method(self, request, *args, **kwargs)
            if response.status_code == 200:
                # Only cache 200 OK JSONs
                cache.set(cache_key, response.data, timeout=timeout)
            return response

        return _wrapped_view

    return decorator


class HealthCheckView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT PostGIS_Full_Version();')
                cursor.fetchone()
        except DatabaseError as e:
            return Response({'status': 'error', 'db': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class POIViewSet(viewsets.ModelViewSet):
    queryset = PointOfInterest.objects.all().prefetch_related('translations')
    serializer_class = PointOfInterestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOperatorOrReadOnly]

    @action(detail=False, methods=['get'])
    @cache_response(timeout=120)
    def nearby(self, request):
        lon = request.query_params.get('lon')
        lat = request.query_params.get('lat')
        radius = float(request.query_params.get('radius', 2.0))
        if lon is None or lat is None:
            return Response({'detail': 'lon and lat required'}, status=400)
        qs = services.search_pois_within_radius(lon, lat, radius)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    @cache_response(timeout=120)
    def aggregate(self, request, pk=None):
        poi = services.poi_with_aggregate_rating(pk)
        if poi is None:
            return Response({'detail': 'Not found'}, status=404)
        data = self.get_serializer(poi).data
        data['avg_rating'] = getattr(poi, 'avg_rating', None)
        return Response(data)

    def perform_create(self, serializer):
        poi = serializer.save(operator=self.request.user)
        translations = self.request.data.get('translations')
        if translations:
            for lang, data in translations.items():
                services.create_poi_translations_only(poi, {lang: data})

    def perform_update(self, serializer):
        poi = self.get_object()
        services.update_poi(poi, **serializer.validated_data)
        serializer.save()

    def perform_destroy(self, instance):
        services.delete_poi(instance)


class AttractionScheduleViewSet(viewsets.ModelViewSet):
    queryset = AttractionSchedule.objects.select_related('poi').all()
    serializer_class = AttractionScheduleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOperatorOrReadOnly]

    def perform_create(self, serializer):
        poi = get_object_or_404(PointOfInterest, pk=self.request.data.get('poi'))
        instance = services.create_schedule(
            poi,
            serializer.validated_data['start'],
            serializer.validated_data['end'],
            serializer.validated_data['total_capacity'],
            serializer.validated_data.get('remaining_capacity'),
            serializer.validated_data.get('is_active', True),
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        schedule = self.get_object()
        services.update_schedule(schedule, **serializer.validated_data)
        serializer.save()

    def perform_destroy(self, instance):
        services.delete_schedule(instance)


class ItineraryViewSet(viewsets.ModelViewSet):
    queryset = Itinerary.objects.all().prefetch_related('items', 'items__poi', 'items__poi__translations')
    serializer_class = ItinerarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        stats = services.get_itinerary_stats(pk)
        return Response(stats)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItineraryItemViewSet(viewsets.ModelViewSet):
    queryset = ItineraryItem.objects.all().select_related('poi')
    serializer_class = ItineraryItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        iti = get_object_or_404(Itinerary, pk=self.request.data.get('itinerary'))
        try:
            services.add_itinerary_item(
                iti,
                serializer.validated_data['poi'],
                serializer.validated_data['date'],
                serializer.validated_data['start_time'],
                serializer.validated_data['end_time'],
                serializer.validated_data.get('order'),
                just_validate=True,
            )
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        serializer.save(itinerary=iti)

    def perform_destroy(self, instance):
        services.remove_itinerary_item(instance)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().select_related('itinerary_item', 'schedule')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        services.create_booking(
            self.request.user,
            serializer.validated_data['itinerary_item'],
            serializer.validated_data['schedule'],
            serializer.validated_data['seats'],
        )
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        services.cancel_booking(instance)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('poi')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review, created = services.submit_review(
            self.request.user,
            serializer.validated_data['poi'],
            serializer.validated_data['rating'],
            serializer.validated_data['text'],
        )
        response_serializer = self.get_serializer(review)

        if created:
            response_status = status.HTTP_201_CREATED
        else:
            response_status = status.HTTP_200_OK

        return Response(response_serializer.data, status=response_status)
