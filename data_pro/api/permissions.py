from rest_framework import permissions

class IsClientAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow client admins to edit, but allow anyone to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.user_type in ['CLIENT_ADMIN', 'SUPERADMIN']

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.user_type in ['CLIENT_ADMIN', 'SUPERADMIN']