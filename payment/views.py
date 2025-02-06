from rest_framework.generics import RetrieveUpdateAPIView
from .serializers import CheckoutSerializer
from orders.models import Order
from orders.permissions import IsOrderByBuyerOrAdmin
from .permissions import IsOrderPendingWhenCheckout
from django.db import transaction
from rest_framework.exceptions import APIException
from users.exceptions import InternalServerErrorException


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
