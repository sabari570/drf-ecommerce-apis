from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import CartItem
from django.utils.translation import gettext_lazy as _


class OrderItemSerializer(serializers.ModelSerializer):
    '''
    Serializer class for serializing the order items
    '''
    price = serializers.CharField(source="product.price", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_desc = serializers.CharField(source="product.desc", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_name",
            "product_desc",
            "price",
            "quantity",
            "cost",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("order",)


class OrderReadSerializer(serializers.ModelSerializer):
    '''
    Serialzier class for serializing the Orders
    '''
    buyer = serializers.CharField(source="buyer.get_full_name", read_only=True)
    order_items = OrderItemSerializer(read_only=True, many=True)
    total_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "buyer",
            "shipping_address",
            "billing_address",
            "order_items",
            "total_cost",
            "status",
            "created_at",
            "updated_at",
        )

    def get_total_cost(self, obj):
        return obj.total_cost


class OrderWriteSerializer(serializers.ModelSerializer):
    '''
    Serializer class for creating orders and order items

    Shipping address, Billing address are not included here
    They will be created/updated on checkout
    '''
    buyer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ("id", "buyer",
                  "created_at", "updated_at")

    def create(self, validated_data):
        # select_related():
        #   * This optimizes database queries by using JOINs instead of making separate queries.
        #   * Instead of fetching each Product separately for every CartItem, Django fetches all data in a single SQL query.
        #   * It is used when there is a ForeignKey relationship between CartItem and Product.

        # prefetch_related():
        #  When you have a ManyToManyField or reverse ForeignKey, Django does separate queries and handles joins in Python.
        user = self.context["request"].user
        cart_items = CartItem.objects.filter(
            cart__user=user).select_related("product")

        if not cart_items.exists():
            raise serializers.ValidationError({
                "detail": _("Your cart is empty, Can't place an order.")
            })

        # Checking if a pending order already exists
        order_instance, created = Order.objects.get_or_create(
            buyer=user, status="P")

        # Get the exiting products that are present in the order items
        # a dictionary like: { <product_id>: <order_item1> }
        existing_products = {
            order_item.product.id: order_item for order_item in order_instance.order_items.all()}

        new_order_items = []

        # To track the product ids being added to the order from the cart
        cart_product_ids = set()

        for item in cart_items:
            cart_product_ids.add(item.product.id)
            if item.product.id in existing_products:
                # Update the quantity to match the lastest cart quantity
                existing_order_item = existing_products[item.product.id]
                # Update the existing_order_item quantity
                existing_order_item.quantity = item.quantity
                # Saving the order item
                existing_order_item.save()
            else:
                new_order_items.append(
                    OrderItem(
                        order=order_instance,
                        product=item.product,
                        quantity=item.quantity,
                    )
                )

        # Now bulk saving all the order items
        if new_order_items:
            OrderItem.objects.bulk_create(new_order_items)

        # Now, remove any order items from the order that are no longer in the cart
        # These are products that were previously ordered but now they are removed from the cart

        # product__id__in:
        #   * This is a query lookup syntax in Django that is used to filter objects based on a relationship.
        #   * product: This refers to a related model field on the OrderItem model
        #   * id: This is the field in the Product model that holds the unique identifier of each product.
        #   * __in: This is a lookup operator that allows you to filter for records where a field matches any value in a provided list or set.
        order_instance.order_items.exclude(
            product__id__in=cart_product_ids
        ).delete()

        return order_instance
