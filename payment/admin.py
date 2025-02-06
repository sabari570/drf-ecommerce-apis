from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "get_buyer_name",
        "payment_option",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "payment_option", "created_at")
    search_fields = ("order__id", "order__buyer__first_name",
                     "order__buyer__last_name")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    # Displays the buyer name on the table
    def get_buyer_name(self, obj):
        return obj.order.buyer.get_full_name()

    get_buyer_name.short_description = "Buyer Name"
