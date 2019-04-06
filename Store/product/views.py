from django.shortcuts import render

# Create your views here.
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from product import models

class ProductListView(ListView):
    template_name = "product/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(
            models.ProductTag, slug=tag
            )
        if self.tag:
            products = models.Product.objects.active().filter(
                tags=self.tag
            )
        else:
            products = models.Product.objects.active()
        return products.order_by("name")