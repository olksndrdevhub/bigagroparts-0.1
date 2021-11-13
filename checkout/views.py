from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib.auth import get_user

from xhtml2pdf import pisa

from .forms import BillingForm
from .models import BillingAddress
from core.models import Order
from .admin import link_callback







def checkout(request):
    user = get_user(request)
    form = BillingForm(initial={
            'email': user.email,
            'phone': user.phone_number})

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if len(order_qs) != 0:
        order = order_qs[0]
        order_code = order.id
        order_items = order.items.all()
        order_total = order.get_total()
        context = {
            'form': form,
            'order_items': order_items,
            'order_total': order_total
        }
    else:
        return redirect('/')

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            print('form valid')
        billingaddress = BillingAddress()
        billingaddress.user = request.user
        billingaddress.order = order
        billingaddress.total_price = order_total
        billingaddress.delivery_method = form.data['delivery_method']
        billingaddress.nova_poshta = form.data['nova_poshta']
        billingaddress.city = form.data['city']
        billingaddress.landmark = form.data['landmark']
        billingaddress.phone = form.data['phone']
        billingaddress.email = form.data['email']
        billingaddress.address = form.data['address']
        billingaddress.payment_method = form.data['payment_method']
        print(form.data['payment_method'])
        print(form.data['delivery_method'])       
        billingaddress.save()
        order.ordered = True
        order.save()

        return render(request, 'checkout_success.html')

    return render(request, 'index.html', context)



def generate_invoice_in_cabinet(request, *args, **kwargs):
    user = get_user(request)
    order_id = kwargs['order_id']
    order = BillingAddress.objects.get(order_id=order_id)

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

