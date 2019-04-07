from django.contrib import admin

from shoppingcart import models

# Register your models here.
class BasketLineInline(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ("product",)

@admin.register(models.Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)

class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("product",)

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (OrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                "billing_name",
                "billing_address1",
                "billing_address2",
                "billing_zip_code",
                "billing_city",
                "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
            "fields": (
                "shipping_name",
                "shipping_address1",
                "shipping_address2",
                "shipping_zip_code",
                "shipping_city",
                "shipping_country",
                )
            },
        ),
    )