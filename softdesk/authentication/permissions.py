from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Permission that allows users to update or delete only their own account.
    Everyone can read (safe methods).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
