from rest_framework import permissions


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.author
        return True


class IsNotAuth(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated

