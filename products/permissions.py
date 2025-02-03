from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSellerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return request.method and (obj.seller == request.user or request.user.is_admin)
