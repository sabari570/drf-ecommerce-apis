from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class IsOrderOrPaymentAlreadyConfirmed(APIException):
    status_code = 403
    default_detail = _(
        "This order/payment is already confirmed. You cannot proceed further")
    default_code = "order_or_payment not allowed"
