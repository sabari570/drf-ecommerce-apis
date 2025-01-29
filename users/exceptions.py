# This File is used to create Custom exceptions
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class AccountNotRegisteredException(APIException):
    status_code = 404
    default_detail = _("The account is not registered")
    default_code = 'non-registered-account'


class InternalServerErrorException(APIException):
    status_code = 404
    default_detail = _("Internal server occured. Something went wrong")
    default_code = 'internal-server-error'
