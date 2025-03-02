from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order
from cart.models import CartItem
from .permissions import IsOrderByBuyerOrAdmin, CanUpdateOrderPermission, IsStaffForOrderDeletion
from .serializers import OrderReadSerializer, OrderWriteSerializer
from django.db import transaction
from rest_framework.exceptions import APIException
from users.exceptions import InternalServerErrorException

# Inorder to manually add another custom endpoint in a viewset
from rest_framework.decorators import action


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsOrderByBuyerOrAdmin, CanUpdateOrderPermission]

    # This line only allows the GET, POST, and DELETE route for this view PUT and PATCH requests are not allowed
    http_method_names = ["get", "post", "delete"]

    # Standard approach to apply a custom permission inorder to restrict the access to only selected endpoints.
    def get_permissions(self):
        """
        Apply custom permissions to restrict order deletion to staff users only.
        """
        # Apply IsStaffForOrderDeletion only for the destroy action (standard delete)
        if self.action == "destroy":
            return [IsStaffForOrderDeletion()]

        # In Django REST Framework (DRF), the @action decorator creates a custom view for that specific endpoint.
        # Even though it's a DELETE request, it's not considered part of the default destroy action (which is tied directly to the model instance).
        # This is how we apply the same permission to the custom decorator we created as well
        # This Restricts the cancel order feature to be only accessible by staff_users
        # if self.action == "cancel":
        #     return [IsStaffForOrderDeletion()]

        # For other actions, apply the default permissions
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Dynamically filter orders based on query parameters: status.
        If no status is provided, return all orders for the user.
        """
        user = self.request.user
        status_filter = self.request.query_params.get("status", None)
        queryset = Order.objects.filter(
            buyer=user).prefetch_related("order_items__product")

        if status_filter:
            allowed_statuses = [Order.PENDING,
                                Order.COMPLETED, Order.CANCELLED]
            if status_filter in allowed_statuses:
                queryset = queryset.filter(status=status_filter)

        return queryset

    def get_serializer_class(self):
        if self.action in ("create"):
            return OrderWriteSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                return serializer.save()
        except APIException as e:
            raise e
        except Exception as e:
            print("Error while converting cart to orders: ", e)
            raise InternalServerErrorException()

    # This is how we write a custom endpoint inside a viewset inorder to perform additional functions
    # When detail=True, the action will be applied to a single instance of the model.
    # This means that the action is tied to a specific object (the object identified by the URL parameter, typically the primary key of the object).
    @action(detail=True, methods=['delete'])
    def cancel(self, request, pk=None):
        '''
        Custom action to cancel an order
        PATH: /api/orders/<int:id>/cancel/
        '''
        # Gets the order object
        order = self.get_object()
        if order.status != Order.PENDING:
            return Response(
                {"detail": "This order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark the order status as Canceled
        order.status = Order.CANCELLED
        order.save()

        return Response(
            {"detail": "Order has been cancelled."},
            status=status.HTTP_200_OK,
        )
