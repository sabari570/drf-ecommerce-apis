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


class InvalidCredentialExceptions(APIException):
    status_code = 401
    default_detail = _("Wrong email/phone number or password")
    default_code = 'invalid-credential'


class AccountDisabledException(APIException):
    status_code = 403
    default_detail = _("User account is disabled")
    default_code = 'account-disabled'


class TokenBlackListedException(APIException):
    status_code = 401
    default_detail = _("This token is blacklisted.")
    default_code = 'blacklisted-token'
