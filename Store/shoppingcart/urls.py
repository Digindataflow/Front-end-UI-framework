from django.urls import re_path
from shoppingcart import views

urlpatterns = [
    re_path(
        r"^add_to_basket/$",
        views.add_to_basket,
        'add_to_basket'
    ),
    re_path(
        r'^items/$',
        views.manage_basket,
        'basket_items',
    )
]