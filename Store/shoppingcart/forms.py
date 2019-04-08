from django.forms import inlineformset_factory
from django import forms

from shoppingcart import models, widgets
from account.models import Address

BasketLineFormSet = inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=("quantity",),
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)

class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(
        queryset=None)
    shipping_address = forms.ModelChoiceField(
        queryset=None)
    def __init__(self, user, *args, **kwargs):
        super(). __init__(*args, **kwargs)
        queryset = Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset

class PeriodSelectForm(forms.Form):
    PERIODS = ((30, "30 days"), (60, "60 days"), (90, "90 days"))
    period = forms.TypedChoiceField(
        choices=PERIODS, coerce=int, required=True
    )