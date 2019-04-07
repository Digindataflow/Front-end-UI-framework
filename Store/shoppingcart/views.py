from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render

from shoopingcart import models, forms

def add_to_basket(request):
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
    basket = models.Basket.objects.create(user=user)
    request.session["basket_id"] = basket.id
    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("product", args=(product.slug,))
    )

def manage_basket(request):
    template_name = "shoopingcart/basket.html"
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