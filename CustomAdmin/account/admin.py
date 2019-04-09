from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm
)
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext, gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django import forms
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
# Register your models here.

class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    email1 = forms.CharField(
        label=_("Email"),
        strip=True,
    )
    email2 = forms.CharField(
        label=_("Email confirmation"),
        strip=True,
        help_text=_("Enter the same Email as before, for verification."),
    )

    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'user_permissions')

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1")
        email2 = self.cleaned_data.get("email2")
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return email2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email1')
        user.username = self.cleaned_data.get('email1')
        user.set_password(User.objects.make_random_password(32))
        if commit:
            user.save()
        print(user._password)
        return user

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # User model has a lot of fields, which is why we are
    # reorganizing them for readability
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'groups')}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("email1", "email2", 'first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'groups')}),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        'is_active',
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    add_form = UserCreationForm
