from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from django.conf import settings

User = get_user_model()


class PhoneNumberAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Parse the given number
            number = phonenumbers.parse(
                username, settings.PHONENUMBER_DEFAULT_REGION)
            # Check whether the number is valid
            if not phonenumbers.is_valid_number(number):
                return
            try:
                user = User.objects.get(phone__phone_number=number)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
        except NumberParseException:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
