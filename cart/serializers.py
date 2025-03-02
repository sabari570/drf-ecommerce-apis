from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


class CartItemReadSerializer(serializers.ModelSerializer):
    """
    This serializer is used for reading the individual cart items data.
    """

    product_name = serializers.CharField(source="product.name", read_only=True)
    product_desc = serializers.CharField(source="product.desc", read_only=True)
    price = serializers.CharField(source="product.price", read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_name",
            "product_desc",
            "quantity",
            "price",
            "cost",
        )


class CartItemWriteSerializer(serializers.ModelSerializer):
    """
    This serializer is used for writing and modifying the individual cart items data.
    """

    price = serializers.CharField(source="product.price", read_only=True)
    product_desc = serializers.CharField(source="product.desc", read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=True
    )

    class Meta:
        model = CartItem
        fields = (
            "id",
            "cart",
            "product",
            "product_desc",
            "quantity",
            "price",
            "cost",
        )
        read_only_fields = (
            "cart",
            "price",
        )

    def validate(self, validated_data):
        """
        Validate the cart items, check stock and user-specific conditions
        """
        order_quantity = validated_data.get("quantity", 1)
        # Because the product id can be changed in the request so instead we get the product quantity directly
        # from the product that is already present in the cart while updating
        if self.instance:
            product_quantity = self.instance.product.quantity
        else:
            product_quantity = validated_data.get("product").quantity

        if order_quantity > product_quantity:
            error = {"quantity": _(
                "Requested quantity exceeds available stock.")}
            raise serializers.ValidationError(error)
        return validated_data

    def create(self, validated_data):
        user = self.context["request"].user
        product_data = validated_data.get("product")
        if CartItem.objects.filter(cart=user.cart, product=product_data).first():
            error = {"detail": _("The product is already added to cart")}
            raise serializers.ValidationError(error)
        cartItem_instance = CartItem.objects.create(
            cart=user.cart, product=product_data)
        return cartItem_instance

    def update(self, instance, validated_data):
        # remove the product data as we dont want to update the product id
        validated_data.pop("product", None)

        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()
        return instance


class CartReadSerializer(serializers.ModelSerializer):
    """
    This serializer is used to read the cart data.
    """

    cart_items = CartItemReadSerializer(read_only=True, many=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "cart_items",  # This will include the cart items that each cart is linked to via ForeignKey of the CartItem table
            "total_cost",
            "created_at",
            "updated_at",
        )

    def get_total_cost(self, obj):
        """
        This function return the total cost of the cartItems
        """
        return obj.total_cost
