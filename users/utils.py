from .models import PhoneNumber
from django.contrib.auth import get_user_model
from collections.abc import Iterable

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


# Function to get the insufficient products name
def get_insufficient_products(items):
    '''
    Returns a list of product names where the ordered/cart quantity 
    is greater than the available product stock.

    Args:
        items (iterable): An iterable of cart/order items with 'product' and 'quantity' attributes.

    Returns:
        list: List of product names with insufficient stock.
    '''
    if not isinstance(items, Iterable):
        raise ValueError(
            "Expected an iterable of cart/order items, but got a non-iterable object.")
    return [
        item.product.name for item in items if item.quantity > item.product.quantity
    ]
