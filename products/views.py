from .serializers import ProductReadSerializer, ProductWriteSerializer, ProductCategorySerializer
from rest_framework import viewsets
from .models import Product, ProductCategory
from rest_framework import permissions
from .permissions import IsSellerOrAdmin


class ProductCategoryViewSet(viewsets.ModelViewSet):
    '''
    This Viewset is for the CRUD operations of ProductCategories
    '''
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    '''
    Viewset for products CRUD operations.
    This is the one which suits the URLs generated from DefaultRouter
    '''
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "delete"):
            return ProductWriteSerializer
        else:
            return ProductReadSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action in ("update", "partial_update", "delete"):
            return [IsSellerOrAdmin()]
        else:
            return [permissions.AllowAny()]
