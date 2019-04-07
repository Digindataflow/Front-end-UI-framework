from django.contrib import admin
from django.urls import re_path

from product import views

urlpatterns = [
    re_path(
        r"products/(?P<tag>\w+)/",
        views.ProductListView.as_view(),
        name="product_list",
    ),
    re_path(
        r"^product/(?P<slug>\w+)/$",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
]