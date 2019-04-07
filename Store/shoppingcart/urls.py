from django.urls import re_path
from shoppingcart import views

urlpatterns = [
    re_path(
        r"^add_to_basket/$",
        views.add_to_basket,
        name='add_to_basket'
    ),
    re_path(
        r'^items/$',
        views.manage_basket,
        name='basket_items',
    ),
    re_path(
        r"^address_select/$",
        views.AddressSelectionView.as_view(),
        name="address_select",
    ),
    re_path(
        r"^done/$",
        views.CheckoutDoneView.as_view(),
        name="checkout_done",
    ),
]