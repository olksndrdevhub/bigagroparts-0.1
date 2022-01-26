from django import template
from core.models import Cart

register = template.Library()


@register.filter
def cart_total(session):
    cart_qs = Cart.objects.filter(id=session.get('cart_id'), ordered=False)

    if cart_qs.exists():
        return cart_qs[0].items.count()
    else:
        return 0
