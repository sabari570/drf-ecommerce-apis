from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem

# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_cost",
                    "created_at", "updated_at")  # Fields displayed in list
    # Allow searching by username and email
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at",)  # Filter by creation date
    # Prevent modification of calculated total cost
    readonly_fields = ("total_cost",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "cost", "created_at")
    search_fields = ("cart__user__username", "product__name")
    list_filter = ("created_at", "product")
    readonly_fields = ("cost",)
