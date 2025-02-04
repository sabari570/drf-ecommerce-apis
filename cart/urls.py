from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet

app_name = "cart"

router = DefaultRouter()

router.register(r"cartItems", CartItemViewSet)
router.register(r"", CartViewSet)

urlpatterns = [
    path("", include(router.urls))
]
