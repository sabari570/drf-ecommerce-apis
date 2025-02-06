from rest_framework.permissions import BasePermission
from orders.models import Order


class IsOrderPendingWhenCheckout(BasePermission):
    """
    Check the status of order is pending or completed before updating instance
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET",):
            return True
        return obj.status == Order.PENDING
