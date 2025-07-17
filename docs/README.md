# Localized Tour Itinerary & Booking API

## Overview
A backend service for travelers to find geotagged attractions, build day-by-day itineraries, and book time-slot attractions—with full RESTful API, authentication, geo-search, reviews/ratings, advanced statistics and robust concurrency.

## Data Model

- **PointOfInterest:** Geotagged location, operator (owner), name; supports multilingual translations (`POITranslation`).
- **POITranslation:** Contains (poi, language_code, name, description) for i18n.
- **AttractionSchedule:** Linked to POI, defines time-slot & total/remaining capacity; availability is locked on booking using transactions.
- **Itinerary:** Owned by user; holds trip name, dates.
- **ItineraryItem:** Ordered items with reference to POI, date, start/end times; supports overlap prevention.
- **Booking:** User's admission to a schedule (attraction+slot), tracks seat count, payment/ref placeholder, and status (pending/confirmed/cancelled) using row-level locking (`select_for_update`).
- **Review:** One per user per POI; stores rating and text, used for aggregate POI rating view.

## Features

- **CRUD** for all core resources (POI, Itinerary, Booking, etc.).
- **Multilingual content:** via POITranslation and internationalization middleware.
- **Full-text and geo-radius search:** `/api/pois/nearby/` uses PostGIS and custom QuerySet; results sorted by distance.
- **Itinerary builder:** Days, ordered items with time windows (overlap validation and prevention in service layer).
- **Attraction schedules:** Time slots with real-time capacity & transactional seat lock on booking, preventing overbooking.
- **Secure booking endpoint:** Payment stub, atomic savepoint, email stub.
- **Reviews & aggregate ratings:** Review endpoint and `POI.aggregate` for average rating annotation.
- **Advanced statistics:** `/api/itineraries/<id>/stats/` returns total walking distance (km, Haversine) and daily counts using CTEs/window queries.
- **Authentication:** DRF TokenAuthentication, permissions distinguish public access from operator/owner update.
- **Rate limiting & caching:** Public endpoints leverage Redis via per-view caching decorators for hot/nearby/aggregate POI.
- **API schema:** Automatic via drf-spectacular (OpenAPI 3).
- **Logging:** structlog-based JSON logs.
- **Pagination & filtering:** via DRF and django-filter.
- **Internationalization:** Accept-Language and ugettext_lazy. Response content can be localized.

## Architecture & Patterns
- **Layered Architecture:** Models, services (all business logic), serializers, API views/controllers.
- **Service Pattern:** Pure classes/functions in `services.py` encapsulate all rules—views/controllers never access models directly.
- **Custom Managers/QuerySets:** For complex geo and aggregation queries.
- **Transactional Operations:** Bookings use `transaction.atomic`/`select_for_update` for concurrency.
- **DRF Viewsets & Serializers:** All resources exposed via modern REST.

## Getting Started
- Bring up with Docker Compose; DB and Redis included.
- Endpoints: `/api/`—see [drf-spectacular OpenAPI docs](#) or `/api/schema/` when enabled.
- Run tests: `make test` (Pytest+pytest-django+FactoryBoy, >90% coverage), linters with `make lint`.

## Advanced Operations
- **POI Radius search:** `/api/pois/nearby/?lon=<lon>&lat=<lat>&radius=<km>`
- **Stats endpoint:** `/api/itineraries/<id>/stats/` supplies CTE-based occupancy & walking distance.
- **Operator-only mutability:** Non-owners cannot mutate POI, schedule, itinerary.

## Requirements Covered
- Layered service DRY/clean design, DRF Token auth and permissions, full postgis support, Redis caching, DRF schema, advanced locking & concurrency, true CTE window queries using only supported dependencies. 

## Tech Stack
- **Python 3.11**, **Django 4.x**, **DRF**, **Postgres+PostGIS 15**, **Redis**, **drf-spectacular**, **structlog**, **django-filter**, **pytest**, **factory_boy**

---
Questions or suggestions? Contact the project technical lead.
