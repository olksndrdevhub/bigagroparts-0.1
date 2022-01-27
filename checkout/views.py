from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required

from xhtml2pdf import pisa

from .forms import BillingForm
from .models import Order
from core.models import Cart
from .admin import link_callback


def checkout(request):
    user = get_user(request)
    cart_id = request.session.get('cart_id')
    initial = {}
    if user.is_authenticated:
        initial={
            'email': user.email,
            'phone': user.phone_number,
            'customer_name': user.last_name+' '+user.first_name+' '+user.second_name}
    form = BillingForm(initial=initial)

    cart_qs = Cart.objects.filter(id=cart_id, ordered=False)
    if len(cart_qs) != 0:
        cart = cart_qs[0]
        order_code = cart.id
        order_items = cart.items.all()
        order_total = cart.get_total()
        context = {
            'form': form,
            'order_items': order_items,
            'order_total': order_total,
            'order_code': order_code
        }
    else:
        return redirect('/')

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            print('form valid')
        order = Order()
        order.user = request.user if user.is_authenticated else None
        order.cart = cart
        order.total_price = order_total
        order.delivery_method = form.data['delivery_method']
        order.nova_poshta = form.data['nova_poshta']
        order.customer_name = form.data['customer_name']
        order.city = form.data['city']
        order.landmark = form.data['landmark']
        order.phone = form.data['phone']
        order.email = form.data['email']
        order.address = form.data['address']
        order.payment_method = form.data['payment_method']
        print(form.data['payment_method'])
        print(form.data['delivery_method'])
        order.save()
        cart.ordered = True
        cart.order_status = Cart.ORDER_ACCEPTED
        cart.save()

        return render(request, 'checkout_success.html')

    return render(request, 'index.html', context)


@login_required
def generate_invoice_in_cabinet(request, *args, **kwargs):
    # user = get_user(request)
    order_code = kwargs['order_code']
    order = Order.objects.get(cart_id=order_code)

    template_path = 'pdf/sales-invoice.html'
    context = order.generate_invoice_context(request)
    bayer = context['bayer']
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_orderid_{order_code}_user_{bayer}.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create PDF
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback,
    )

    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse(f'We had some errors <pre>{html}</pre>')

    return response
