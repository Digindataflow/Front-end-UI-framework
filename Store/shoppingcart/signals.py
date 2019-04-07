from django.contrib.auth.signals import user_logged_in
from shoppingcart.models import Basket

@receiver(user_logged_in)
def merge_baskets_if_found(sender, user, request,**kwargs):
    anonymous_basket = getattr(request, "basket", None)
    if anonymous_basket:
        try:
            loggedin_basket = Basket.objects.get(
                user=user, status=Basket.OPEN
            )
            for line in anonymous_basket.basketline_set.all():
                line.basket = loggedin_basket
                line.save()
                anonymous_basket.delete()
                request.basket = loggedin_basket
                logger.info(
                    "Merged basket to id %d", loggedin_basket.id
                )
        except Basket.DoesNotExist:
            anonymous_basket.user = user
            anonymous_basket.save()
            logger.info(
                "Assigned user to basket id %d",
                anonymous_basket.id,
            )

