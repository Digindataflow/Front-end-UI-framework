from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView
from shoppingcart import models, forms

def add_to_basket(request):
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )

    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id
    else:
        basket = request.basket

    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("product_detail", args=(product.slug,))
    )

def manage_basket(request):
    template_name = "shoppingcart/basket.html"
    if not request.basket:
        return render(request, template_name, {"formset": None})
    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket
        )
    if request.basket.is_empty():
        return render(request, template_name, {"formset": None})
    return render(request, template_name, {"formset": formset})

class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "shoppingcart/address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy('checkout_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data['billing_address'],
            form.cleaned_data['shipping_address']
        )
        return super().form_valid(form)

class CheckoutDoneView(TemplateView):
    template_name = "shoppingcart/order_done.html"