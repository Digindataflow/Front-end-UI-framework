from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_save, post_save
from shoppingcart.models import Basket, OrderLine, Order

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

@receiver(post_save, sender=OrderLine)
def orderline_to_order_status(sender, instance, **kwargs):
    if not instance.order.lines.filter(status__lt=OrderLine.SENT).exists():
        logger.info(
            "All lines for order %d have been processed. Marking as done.",
            instance.order.id
        )
        instance.order.status = Order.DONE
        instance.order.save()