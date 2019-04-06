from django.contrib import admin
from django.urls import path

from product import views

urlpatterns = [
    path(
        "products/<slug:tag>/",
        views.ProductListView.as_view(),
        name="product_list",
    ),
    path(
        "product/<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
]