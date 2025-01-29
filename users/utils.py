from .models import PhoneNumber
from django.contrib.auth import get_user_model

User = get_user_model()

def send_or_resend_sms(phone_number):
    # Filter the user and get the user who has this phone number
    filtered_user = User.objects.filter(
        phone__phone_number=phone_number).first()
    sms_verification = PhoneNumber.objects.filter(
        user=filtered_user, is_verified=False).first()
    if sms_verification:
        return sms_verification.send_confirmation()
    return None
