from rest_framework import viewsets
from .serializers import CartItemReadSerializer, CartItemWriteSerializer, CartReadSerializer
from rest_framework import permissions
from .models import Cart, CartItem
from .permissions import IsNotSellerOfProduct


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    # permission_classes = [IsNotSellerOfProduct]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "delete"):
            return CartItemWriteSerializer
        else:
            return CartItemReadSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartReadSerializer
    # Inorder to disable pagination in this view
    pagination_class = None

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
