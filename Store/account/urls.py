from django.urls import re_path

from account import views

urlpatterns = [
    re_path(r'^signup/$', views.SignupView.as_view(), name="signup"),
    re_path(r"^login/$", views.LoginView.as_view(), name="login",),
    re_path(
        r"^address/$",
        views.AddressListView.as_view(),
        name="address_list",
    ),
    re_path(
        r"^address/create/$",
        views.AddressCreateView.as_view(),
        name="address_create",
    ),
    re_path(
        r"^address/(?P<pk>\d+)/$",
        views.AddressUpdateView.as_view(),
        name="address_update",
    ),
    re_path(
        r"^address/(?P<pk>\d+)/delete/$",
        views.AddressDeleteView.as_view(),
        name="address_delete",
    ),
]
