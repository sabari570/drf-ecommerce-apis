from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth import get_user_model
from products.models import Product
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Cart(models.Model):
    '''
    This is a cart model that belongs to each users logged in
    '''
    user = models.OneToOneField(
        User, related_name='cart', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Cart")

    def __str__(self):
        return f"Cart of {self.user.get_full_name()}"

    # The @cached_property is given because it improves performance:
    # If a method is called multiple times within a single request,
    # the computed result is stored and reused, rather than recalculating it each time.
    # Without @cached_property, every time cart.total_cost is accessed, Django would query the database and iterate through the cart_items again.
    @cached_property
    def total_cost(self):
        '''
        Returns the total cost of the cart items in the cart.
        '''
        # This takes the sum and rounds of the decimal point value upto 2 decimal places
        return round(sum(item.cost for item in self.cart_items.all()), 2)

    @cached_property
    def total_cartitems(self):
        '''
        Returns the total items in the cart
        '''
        return sum(item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    '''
    This is the cart item model, which details out each item in a cart
    '''
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='cart_product_item')
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        # Ensures a product appears only once per cart
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.get_full_name()}'s cart"

    @cached_property
    def cost(self):
        '''
        This function is used to calculate the total cost of this cart item
        '''
        return round(self.quantity * self.product.price, 2)
