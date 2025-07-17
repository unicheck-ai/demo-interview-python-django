from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # For AttractionSchedule/POI: If related model (itinerary/poi) has user/operator, check recursively;
        # otherwise, fallback to user attr for Itinerary, Review, etc.
        user = getattr(obj, 'user', None)
        if user is not None:
            return user == request.user
        if hasattr(obj, 'itinerary') and hasattr(obj.itinerary, 'user'):
            return obj.itinerary.user == request.user
        return False


class IsOperatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        operator = getattr(obj, 'operator', None)
        if operator is not None:
            return operator == request.user
        if hasattr(obj, 'poi') and hasattr(obj.poi, 'operator'):
            return obj.poi.operator == request.user
        return False
