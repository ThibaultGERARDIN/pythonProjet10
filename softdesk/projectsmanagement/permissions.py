from rest_framework import permissions
from .models import ProjectContributor


class IsProjectContributor(permissions.BasePermission):
    """
    Custom permission to only allow contributors to access the project.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user is a contributor of the project.
        """
        if request.user == obj.author:
            return True
        return ProjectContributor.objects.filter(project=obj, user=request.user).exists()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Only the author of the resource can modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
