from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class IsNotSellerOfProduct(BasePermission):
    """
    Permission class to prevent a user from adding their own product to the cart
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        print(request.user)
        print(obj.product.seller)
        if request.user == obj.product.seller:
            raise PermissionDenied(
                _("Adding your own product to the cart is not allowed.")
            )
        return True
