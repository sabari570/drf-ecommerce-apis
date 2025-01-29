from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, PhoneNumber

# Register your models here.

# This is the standard way to register the models inorder to have a well-structured code and cleaner admin panel
# If we just register the models you will not have the FILTER, SEARCH options on the admin panel

# _("User Information") and others in fieldsets → Translatable section headers
# ✔ _("Permissions"), _("Important Dates") → Makes labels translatable

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "firstname",
                    "lastname", "is_active", "is_staff", "date_joined")
    list_filter = (
        ("is_active", admin.BooleanFieldListFilter),
        ("is_staff", admin.BooleanFieldListFilter),
        ("date_joined", admin.DateFieldListFilter),
    )
    search_fields = ("email", "username")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined",)

    # For Translational labels
    fieldsets = (
        (_("User Information"), {
         "fields": ("email", "username", "firstname", "lastname")}),
        (_("Permissions"), {
         "fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important Dates"), {"fields": ("date_joined",)}),
    )


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number", "is_verified", "created_at")
    list_filter = (
        ("is_verified", admin.BooleanFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
    )
    search_fields = ("phone_number", "user__email", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at",)

    fieldsets = (
        (_("Phone Information"), {
         "fields": ("user", "phone_number", "is_verified")}),
        (_("Verification Details"), {"fields": ("security_code", "sent")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )
