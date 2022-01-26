from django import template
from core.models import Order

register = template.Library()


@register.filter
def cart_total(session):
    order = Order.objects.filter(id=session.get('order_id'), ordered=False)

    if order.exists():
        return order[0].items.count()
    else:
        return 0
