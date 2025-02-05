from rest_framework import viewsets, generics, permissions
from .serializers import CartItemReadSerializer, CartItemWriteSerializer, CartReadSerializer
from .models import Cart, CartItem
from .permissions import IsNotSellerOfProduct
from django.utils.translation import gettext_lazy as _
from .exceptions import AddingOwnProductToCartException


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    permission_classes = [IsNotSellerOfProduct]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update", "delete"):
            return CartItemWriteSerializer
        else:
            return CartItemReadSerializer

    # We write this perform_create here beacuse the has_object_permission in the custom permission class does not get executed for POST requests
    # The perform_create method in the view does not replace the serializer's create method; it just adds extra logic before calling serializer.save().
    # It performs additional checks (like ensuring the user isn't the seller).
    # It then calls serializer.save(), which internally invokes the create method inside your serializer.
    def perform_create(self, serializer):
        product = serializer.validated_data.get("product")

        if self.request.user == product.seller:
            raise AddingOwnProductToCartException()

        serializer.save(cart=self.request.user.cart)

# The ReadOnlyModelViewSet:- only allows GET request
class CartListAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartReadSerializer
    # Inorder to disable pagination in this view
    pagination_class = None

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
