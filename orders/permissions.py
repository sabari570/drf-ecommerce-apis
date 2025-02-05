from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission


class IsOrderByBuyerOrAdmin(BasePermission):
    '''
    Check if order is owned by appropriate buyer or admin
    '''

    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return obj.buyer == request.user or request.user.is_staff


class CanUpdateOrderPermission(BasePermission):
    """
    Custom permission to block update actions on the Order model.
    """

    def has_permission(self, request, view):
        if view.action in ['update', 'partial_update']:
            return False
        return True
