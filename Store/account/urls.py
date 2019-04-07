from django.urls import re_path

from account import views

urlpatterns = [
    re_path('^signup/$', views.SignupView.as_view(), name="signup"),
    re_path("^login/$", views.LoginView.as_view(), name="login",),
]
