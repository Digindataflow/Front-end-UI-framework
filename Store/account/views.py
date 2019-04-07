import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views.generic import FormView

from account import forms

logger = logging.getLogger(__name__)

class SignupView(FormView):
    template_name = "account/signup.html"
    form_class = forms.UserCreationForm
    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(
            "New signup for email=%s through SignupView", email
        )
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(
            self.request, "You signed up successfully."
        )
        return response

class LoginView(auth_views.LoginView):
    template_name = "account/login.html"
    form_class = forms.AuthenticationForm
