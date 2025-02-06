from django.db import models
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from products.models import Product
from users.models import Address

User = get_user_model()


class Order(models.Model):
    PENDING = "P"
    COMPLETED = "C"
    CANCELLED = "X"

    STATUS_CHOICES = ((PENDING, _("pending")), (COMPLETED,
                      _("completed")), (CANCELLED, _("cancelled")))

    buyer = models.ForeignKey(
        User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING)
    shipping_address = models.ForeignKey(
        Address, related_name="shipping_orders", on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        Address, related_name="billing_orders", on_delete=models.SET_NULL, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Order of {self.buyer.get_full_name()}"

    @cached_property
    def total_cost(self):
        """
        Total cost of all the items in an order
        """
        return round(sum([order_item.cost for order_item in self.order_items.all()]), 2)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="product_orders", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.buyer.get_full_name()}'s order"

    @cached_property
    def cost(self):
        '''
        This function is used to calculate the total cost of this cart item
        '''
        return round(self.quantity * self.product.price, 2)
