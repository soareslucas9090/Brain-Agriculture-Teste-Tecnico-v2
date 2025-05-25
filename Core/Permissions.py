from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions


class EhAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False

        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, AnonymousUser):
            return False

        return request.user.is_admin


class EhMeuDado(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(request.user, AnonymousUser):
            return False

        return view.get_dono_do_registro()
