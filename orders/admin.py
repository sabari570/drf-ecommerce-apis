from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "total_cost", "status", "shipping_address", "billing_address",
                    "created_at", "updated_at")  # Fields displayed in list
    # Allow searching by username and email
    search_fields = ("buyer__username", "buyer__email")
    list_filter = ("created_at",)  # Filter by creation date
    # Prevent modification of calculated total cost
    readonly_fields = ("total_cost",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "cost", "created_at")
    search_fields = ("order__buyer__username", "product__name")
    list_filter = ("created_at", "product")
    readonly_fields = ("cost",)
