from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow users with user_type='owner' to create flats.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'owner'