from django.urls import include, path
from .views import CheckoutAPIView

app_name = 'payment'

urlpatterns = [
    path("checkout/<int:pk>/", CheckoutAPIView.as_view(), name="checkout"),
]
