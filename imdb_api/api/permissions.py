from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsNotAuth(BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class AdminOnly(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin'


class IsAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT', 'PATCH'):
            if request.user.is_authenticated:
                return request.user.role == 'admin'
        else:
            return True

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or (request.user.is_authenticated and request.user.role == 'admin'):
            return True


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            (request.user == obj.author) or (
                request.user.role in ('admin', 'moderator')))
