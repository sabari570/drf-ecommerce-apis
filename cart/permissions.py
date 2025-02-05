from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from .exceptions import AddingOwnProductToCartException


class IsNotSellerOfProduct(BasePermission):
    """
    Permission class to prevent a user from adding their own product to the cart
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        if request.user == obj.product.seller:
            raise AddingOwnProductToCartException()
        return True
