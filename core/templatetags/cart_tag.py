from django import template
from core.models import Cart

register = template.Library()


@register.filter
def cart_total(request):
    session = request.session
    if request.user.is_authenticated:
        cart_qs = Cart.objects.filter(id=session.get('cart_id'), ordered=False)
        if not cart_qs.exists():
            cart_qs = Cart.objects.filter(user=request.user, ordered=False)
    else:
        cart_qs = Cart.objects.filter(id=session.get('cart_id'), ordered=False)

    if cart_qs.exists():
        if session.get('cart_id') is None:
            session['cart_id'] = cart_qs[0].id
            return cart_qs[0].items.count()
        else:
            return cart_qs[0].items.count()
    else:
        return 0
