Task 1 – Walking-distance numbers look suspicious
------------------------------------------------

Some travellers are complaining that the walking-distance figure inside their daily itinerary report is way too low for the routes they actually take. They compare our number with popular map services and always notice a big gap.

Example: a straight 1-degree move north–south should be a little more than 111 km but the report shows roughly 69 km. The day-by-day occupancy counter is still correct – only the total kilometre estimate is off.

Business impact:
• Marketing highlights the distance summary as a motivating metric; displaying the wrong value makes us look untrustworthy.
• Long-distance walking tours cannot badge “100 km achieved” correctly.

Fixing this is urgent so customers see realistic numbers again.


Task 2 – “One review per user” rule crashes API
-----------------------------------------------

Users are allowed to leave only a single review for each attraction, and if they try again we should simply update their previous rating and text.

Currently, sending a second review request causes the mobile app to receive a 500 server error. For example:
1. POST /api/reviews/   {{rating:3}}
2. POST /api/reviews/   {{rating:5}}

The second call should overwrite the existing review instead of returning an error. This regression blocks users from updating their feedback.

Impact:
• Poor UX – travellers cannot revise outdated ratings after re-visiting an attraction.
• App displays generic error banner which hurts engagement.

Restore smooth update behaviour so repeated submissions replace the old review without any database errors.


Task 3 – Itinerary list endpoint suffers from N+1 database queries
-----------------------------------------------------------------

The itinerary overview endpoint (/api/itineraries/) is getting slower as heavy users add more trips. Investigations reveal an N+1 query pattern: the API makes dozens of individual SQL calls to fetch related itinerary items and their points of interest instead of bundling them efficiently.

Example on staging with just five itineraries (three items each): more than 50 queries are executed for a single request when no caching is enabled. This will not scale once hundreds of itineraries per user exist.

Impact:
• Performance degradation – page takes seconds to load on mid-range phones.
• Database pressure – unnecessary round-trips increase load and cost.

We need to refactor the queryset/serialization pipeline so the same call issues only a handful of queries regardless of item count.


Task 4 – Show translated attraction names based on user language
----------------------------------------------------------------

Our database stores localised names & descriptions for each attraction (POI), but the mobile app still shows the default language even when the user’s phone is set to another locale.

Example: A German visitor with phone language set to “de-DE” requests /api/pois/42/ and still receives “Castle” instead of “Burg”. If the requested language is unavailable we should gracefully fall back to the default name.

Impact:
• International users see untranslated content which feels unprofessional.
• Marketing campaigns promoting multilingual support are undermined.

Update the POI detail (and ideally list) responses so they respect the Accept-Language header and return the matching translation when present.


Task 5 – Deleting an attraction must be reversible (soft-delete)
----------------------------------------------------------------

Tour operators sometimes remove an attraction from public listings by mistake and then call support because all its reviews and schedules are gone. We need a safer mechanism.

Desired behaviour:
• When an operator hits the DELETE button, the record should be marked as “archived” instead of being physically removed from the database.
• Archived POIs must disappear from all regular API queries so travellers cannot see or book them.
• Admins still need to view and restore archived records.

Impact:
• Data loss incidents create frustration and require costly manual restores from backups.
• Support workload increases and SLA targets are missed.

Introduce a soft-delete strategy for POIs (and, ideally, their dependent objects) so operators can undo an accidental removal.
