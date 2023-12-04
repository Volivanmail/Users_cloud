from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # print(request.user)
        # print(request.user.is_admin)
        return request.user and request.user.is_admin

