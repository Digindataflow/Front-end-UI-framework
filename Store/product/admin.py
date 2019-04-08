import logging
from datetime import datetime, timedelta

from django.contrib import admin
from django.db.models import Avg, Count, Min, Sum
from django.db.models.functions import TruncDay
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html

# Register your models here.
from product import models

logger = logging.getLogger(__name__)

def make_active(self, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Mark selected items as active"

def make_inactive(self, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = "Mark selected items as inactive"

@admin.register(models.Product, admin.central_office_admin)
@admin.register(models.Product, admin.main_admin)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'in_stock', 'price')
    list_filter = ('active', 'in_stock', 'date_updated')
    list_editable = ('in_stock', )
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('tags',)
    actions = [make_active, make_inactive]

    # tag slugs also appear in urls, therefore it is a
    # property only owners can change
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ["slug", "name"]
    # This is required for get_readonly_fields to work
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}

@admin.register(models.Product, admin.dispatchers_admin)
class DispatchersProductAdmin(ProductAdmin):
    readonly_fields = ("description", "price", "tags", "active")
    prepopulated_fields = {}
    autocomplete_fields = ()

@admin.register(models.ProductTag, admin.dispatchers_admin)
@admin.register(models.ProductTag, admin.central_office_admin)
@admin.register(models.ProductTag, admin.main_admin)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    # tag slugs also appear in urls, therefore it is a
    # property only owners can change
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return list(self.readonly_fields) + ["slug", "name"]
    # This is required for get_readonly_fields to work
    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}

@admin.register(models.ProductImage, admin.central_office_admin)
@admin.register(models.ProductImage, admin.main_admin)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_tag', 'product_name')
    readonly_fields = ('thumbnail',)
    search_fields = ('product__name',)

    # this function returns HTML for the first column defined
    # in the list_display property above
    def thumbnail_tag(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="%s"/>' % obj.thumbnail.url
            )
        return "-"
    # this defines the column name for the list_display
    thumbnail_tag.short_description = "Thumbnail"

    def product_name(self, obj):
        return obj.product.name
