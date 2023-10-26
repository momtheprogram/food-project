from rest_framework import permissions


class IsOwnerOrAcceptedMethods(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return ((obj.author == request.user)
                or request.method in tuple(permissions.SAFE_METHODS)
                + ('POST',))


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
