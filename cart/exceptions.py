from rest_framework.exceptions import PermissionDenied, APIException
from django.utils.translation import gettext_lazy as _


class AddingOwnProductToCartException(APIException):
    status_code = 403
    default_detail = _("Adding your own product to the cart is not allowed.")
    default_code = "add_to_cart_not_allowed"
