from django.contrib import admin
from django import forms
from shoppingcart import models
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from shoppingcart.forms import PeriodSelectForm

class InvoiceMixin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "invoice/<int:order_id>/",
                self.admin_view(self.invoice_for_order),
                name="invoice",
            )
        ]
        return my_urls + urls

    def invoice_for_order(self, request, order_id):
        order = get_object_or_404(models.Order, pk=order_id)
        if request.GET.get("format") == "pdf":
            html_string = render_to_string(
                "invoice.html", {"order": order}
            )
            html = HTML(
                string=html_string,
                base_url=request.build_absolute_uri(),
            )
            result = html.write_pdf()
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = "inline; filename=invoice.pdf"
            response["Content-Transfer-Encoding"] = "binary"
            with tempfile.NamedTemporaryFile(delete=True) as output:
                output.write(result)
                output.flush()
                output = open(output.name, "rb")
                binary_pdf = output.read()
                response.write(binary_pdf)
                return response
        return render(request, "invoice.html", {"order": order})

# Register your models here.
# The class below will pass to the Django Admin templates a couple
# of extra values that represent colors of headings
class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context["site_header_color"] = getattr(
            self, "site_header_color", None
        )
        context["module_caption_color"] = getattr(
            self, "module_caption_color", None
        )
        return context

# The following will add reporting views to the list of
# available urls and will list them from the index page
class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("orders_per_day/", self.admin_view(self.orders_per_day)),
            path(
                "most_bought_products/",
                self.admin_view(self.most_bought_products),
                name="most_bought_products",
            ),
        ]
        return my_urls + urls

    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (
            models.Order.objects\
                .filter(date_added__gt=starting_day)\
                .annotate(day=TruncDay("date_added"))\
                .values("day")\
                .annotate(c=Count("id"))
        )
        labels = [
            x["day"].strftime("%Y-%m-%d") for x in order_data
        ]
        values = [x["c"] for x in order_data]
        context = dict(
            self.each_context(request),
            title="Orders per day",
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "orders_per_day.html", context
        )

    def most_bought_products(self, request):
        if request.method == "POST":
            form = PeriodSelectForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(days=days)
                data = (
                    models.OrderLine.objects.filter(
                        order__date_added__gt=starting_day
                    )
                    .values("product__name")
                    .annotate(c=Count("id"))
                )
                logger.info(
                    "most_bought_products query: %s", data.query
                )
                labels = [x["product__name"] for x in data]
                values = [x["c"] for x in data]
        else:
            form = PeriodSelectForm()
            labels = None
            values = None

        context = dict(
            self.each_context(request),
            title="Most bought products",
            form=form,
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "most_bought_products.html", context
        )

    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/",
            },
            {
                "name": "Most bought products",
                "link": "most_bought_products/",
            }
        ]
        if not extra_context:
            extra_context = {}
        extra_context = {"reporting_pages": reporting_pages}
        return super().index(request, extra_context)

# Finally we define 3 instances of AdminSite, each with their own
# set of required permissions and colors
class OwnersAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "Store owners administration"
    site_header_color = "black"
    module_caption_color = "grey"

    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_superuser
        )

class CentralOfficeAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "Store central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_employee
        )

class DispatchersAdminSite(ColoredAdminSite):
    site_header = "Store central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"
    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_dispatcher
        )

main_admin = OwnersAdminSite()
central_office_admin = CentralOfficeAdminSite(
    "central-office-admin"
)
dispatchers_admin = DispatchersAdminSite("dispatchers-admin")

class BasketLineInline(admin.TabularInline):
    model = BasketLine
    raw_id_fields = ("product",)

@admin.register(models.Basket, dispatchers_admin)
@admin.register(models.Basket, central_office_admin)
@admin.register(models.Basket, main_admin)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)

class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("product",)

@admin.register(models.Order, main_admin)
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

# Employees need a custom version of the order views because
# they are not allowed to change products already purchased
# without adding and removing lines
class CentralOfficeOrderLineInline(admin.TabularInline):
    model = models.OrderLine
    readonly_fields = ("product",)

@admin.register(models.Order, central_office_admin)
class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
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

# Dispatchers do not need to see the billing address in the fields
@admin.register(models.Order, dispatchers_admin)
class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shipping_name",
        "date_added",
        "status",
    )
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
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
    # Dispatchers are only allowed to see orders that
    # are ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=models.Order.PAID)
