from django.contrib import admin
from .models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "seller",
                    "price", "quantity", "created_at")
    list_filter = ("category", "seller", "created_at")
    search_fields = ("name", "desc", "seller__username")
    ordering = ("-created_at",)
    autocomplete_fields = ("category", "seller")
    list_editable = ("price", "quantity")
    readonly_fields = ("created_at", "updated_at")
