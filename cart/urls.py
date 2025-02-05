from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CartListAPIView, CartItemViewSet

app_name = "cart"

router = DefaultRouter()

router.register(r"", CartItemViewSet)

urlpatterns = [
    path("", CartListAPIView.as_view(), name="cart-list"),
    path("cartItems/", include(router.urls)),
]
