from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib.auth import get_user

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
        initial={'email': user.email, 'phone': user.phone_number}
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
        cart.save()

        return render(request, 'checkout_success.html')

    return render(request, 'index.html', context)


def generate_invoice_in_cabinet(request, *args, **kwargs):
    # user = get_user(request)
    order_id = kwargs['order_id']
    order = Order.objects.get(order_id=order_id)

    template_path = 'pdf/sales-invoice.html'
    context = order.generate_invoice_context(request)
    bayer = order.user
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_orderid_{order_id}_user_{bayer}.pdf"'
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
