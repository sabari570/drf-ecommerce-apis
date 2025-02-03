from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, ProductViewSet

# This is also needed inorder for the urlpatterns in the settings file understand that their is an app
# in the project that accepts those URLs

app_name = "products"

# Here this DefaultRouter is set because this router automatically defines all the endpoints for the products
# like to fetch all products, retrieve a product by id, updating it and deleting it
# all these endpoints will be handled by this router
router = DefaultRouter()

# this URL goes like <domain_name>/api/products/categories/
router.register(r"categories", ProductCategoryViewSet)

# this URL goes like <domain_name>/api/products/
router.register(r"", ProductViewSet)

urlpatterns = [
    # This is how we extract the URLs from router
    path("", include(router.urls))
]
