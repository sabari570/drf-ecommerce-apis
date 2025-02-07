from django.urls import path
from .views import CheckoutAPIView, StripeWebhookAPIView

app_name = 'payment'

urlpatterns = [
    path("checkout/<int:pk>/", CheckoutAPIView.as_view(), name="checkout"),
    path("stripe/webhook/", StripeWebhookAPIView.as_view(), name="stripe_webhook"),
]
