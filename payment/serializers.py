from users.serializers import ShippingAddressSerializer, BillingAddressSerializer
from orders.models import Order
from users.models import Address
from .models import Payment
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from users.utils import get_insufficient_products


class PaymentOptionSerializer(serializers.ModelSerializer):
    '''
    This serializer is for setting up the payment for an Order.

    This is used inside the CheckoutSerializer while checking out of the system inorder to identify which payment mode he user prefers.
    '''
    buyer = serializers.CharField(
        source="order.buyer.get_full_name", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "buyer",
            "payment_option",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "order",)


class CheckoutSerializer(serializers.ModelSerializer):
    '''
    This is the Checkout serializer that actually creates/updates the shipping address or billing address while checkout.

    And alse sets the payment option that we are willing to conduct the payment.
    This is a nested serializer that uses two different models: Order and Payment(PaymentOptionSerializer)
    '''
    shipping_address = ShippingAddressSerializer()
    billing_address = BillingAddressSerializer()
    payment = PaymentOptionSerializer()

    class Meta:
        model = Order
        fields = (
            "id",
            "payment",
            "shipping_address",
            "billing_address",
        )

    # This is the function that saves and links the Address model with the Order model
    # and also it links the Payment and Order model
    def update(self, instance, validated_data):
        order_shipping_address = None
        order_billing_address = None
        order_payment = None

        # PHASE -1: Setting the shipping address or Order
        shipping_address = validated_data.get("shipping_address", None)
        if shipping_address is not None:
            # If the order doesn't have a shipping_address already created then
            if not instance.shipping_address:
                # Creates an instance of the Address
                order_shipping_address = Address(**shipping_address)
                # By calling .save(), you are telling Django to save this object to the corresponding database table (in this case, the Address table).
                # So this line saves this record to the Address table
                order_shipping_address.save()
            else:
                # If the order already has a shipping address created, then update it
                # So first filter out and get the Address instance that is linked with the order and get its shipping address
                # Here we user 'shipping_orders' because Address is connected to Orders via 'shipping_orders'
                existing_shipping_address_instance = Address.objects.filter(
                    shipping_orders=instance.id)
                # Updating the existing address
                existing_shipping_address_instance.update(**shipping_address)
                # We set the updated address to the order_shipping_address variable
                order_shipping_address = existing_shipping_address_instance.first()

        # PHASE -2: Setting the billing address or Order
        billing_address = validated_data.get("billing_address", None)
        if billing_address is not None:
            if not instance.billing_address:
                order_billing_address = Address(**billing_address)
                order_billing_address.save()
            else:
                existing_billing_address_instance = Address.objects.filter(
                    billing_orders=instance.id)
                existing_billing_address_instance.update(**billing_address)
                order_billing_address = existing_billing_address_instance.first()

        # PHASE -3: Setting the payment details of Payment model
        payment = validated_data.get("payment", None)
        if payment is not None:
            if not hasattr(instance, "payment"):
                # Creates a payment instance
                order_payment = Payment(**payment, order=instance)
                # Saves this record to the Payment model
                order_payment.save()
            else:
                # Already a payment option is set now we are updating its value
                # Since we can directly access the order from payment model we pass the whole order instance to it.
                # Earlier in the Address model we passed the instance.id because Address model didnt have the shipping_address fields we had to find the link with the orders table with an order instance id,
                # but in this case the Payment model has an order field in it which needs the entire order instance.
                existing_payment = Payment.objects.filter(order=instance)
                existing_payment.update(**payment)
                order_payment = existing_payment.first()

        # Checking the if the products quantities are sufficient enough to place an order
        insufficent_products = get_insufficient_products(instance.order_items.all())

        if insufficent_products:
            raise serializers.ValidationError({
                "detail": _("The following products are out of stock or insufficient: ") + ", ".join(insufficent_products)
            })

        # These lines connects the Address table and the Order table
        # We update the order table data and connect it with the already created Address records
        if order_shipping_address is not None:
            instance.shipping_address = order_shipping_address
        if order_billing_address is not None:
            instance.billing_address = order_billing_address
        if order_payment is not None:
            # We connect the Order table and Payments table by connecting the instance.payment in Order to the Payment record created
            instance.payment = order_payment

        # Connects & saves in the DB
        instance.save()

        return instance
