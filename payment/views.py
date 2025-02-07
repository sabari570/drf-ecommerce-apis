from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from .serializers import CheckoutSerializer
from orders.models import Order
from orders.permissions import IsOrderByBuyerOrAdmin
from .permissions import IsOrderPendingWhenCheckout
from django.db import transaction
from rest_framework.exceptions import APIException
from users.exceptions import InternalServerErrorException
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from .models import Payment
from django.shortcuts import get_object_or_404
from .exceptions import IsOrderOrPaymentAlreadyConfirmed


class CheckoutAPIView(RetrieveUpdateAPIView):
    '''
    API view that is used for retrieving and updating the shipping address, billing address and payment details of an order.

    You can access this API only if it is a GET request or the UPDATE request provided the order is in PENDING state.
    '''
    queryset = Order.objects.all()
    serializer_class = CheckoutSerializer
    permission_classes = [IsOrderByBuyerOrAdmin]

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            self.permission_classes += [IsOrderPendingWhenCheckout]

        return super().get_permissions()

    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                return super().perform_update(serializer)
        except APIException as e:
            raise e
        except Exception as e:
            print("Error while checkout: ", e)
            raise InternalServerErrorException()


class StripeWebhookAPIView(CreateAPIView):
    '''
    This is the API View that handles the event send from Stripe Webhook after successfull payment.

    After the frontend redirects the app to stripe for payment stripe sends a POST request to this API endpoint,
    and based on the payment success status we update the payment and order status as well as the quantity of the product.
    '''

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                payload = request.data
                event = payload["event"]
                if event["type"] == "checkout.session.completed":
                    session = event["data"]["object"]
                    order_id = session["metadata"]["order_id"]

                    print("Payment successfull")

                    # Finds the payment object with the given order_id or throws an error
                    payment = get_object_or_404(Payment, order=order_id)
                    if payment.status == Payment.COMPLETED:
                        raise IsOrderOrPaymentAlreadyConfirmed()
                    # Updates the status of the payment
                    payment.status = "C"
                    # Saves it in the DB
                    payment.save()

                    order = get_object_or_404(Order, id=order_id)
                    if order.status == Order.COMPLETED:
                        raise IsOrderOrPaymentAlreadyConfirmed()
                    order.status = "C"
                    order.save()

                    # Now time to decrase the product quantity
                    for order_item in order.order_items.all():
                        product = order_item.product
                        product.quantity -= order_item.quantity
                        product.save()

                    return Response({
                        "message": _(f"Payment of {order.total_cost}/- successfull, Your order is on the way!!")
                    }, status=status.HTTP_200_OK)

        except APIException as e:
            raise e
        except Exception as e:
            print(f"Error during stripe payment: {e}")
            raise InternalServerErrorException()
