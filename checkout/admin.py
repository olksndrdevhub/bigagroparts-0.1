import os
from xhtml2pdf import pisa

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls.base import reverse
from django.utils.html import format_html
from django.contrib.auth import get_user_model

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export.widgets import ManyToManyWidget

from .models import Order


User = get_user_model()


class OrderResourse(resources.ModelResource):
    users = fields.Field(widget=ManyToManyWidget(User, field='username'), attribute='users')

    class Meta:
        models = Order


class OrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = OrderResourse
    list_display = ('total_price', 'cart_id', 'user', 'nova_poshta', 'address', 'city', 'landmark', 'phone', 'id', 'order_actions',)
    readonly_fields = ('order_actions',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<id>.+)/generate_invoice_pdf/$',
                self.admin_site.admin_view(self.generate_invoice_pdf),
                name='order-invoice',
            )
        ]
        return custom_urls + urls

    def order_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Згенерувати накладну</a>',
            reverse('admin:order-invoice', args=[obj.id]),
        )

    order_actions.short_description = 'Згенерувати накладну'
    order_actions.allow_tags = True

    def generate_invoice_pdf(self, request, *args, **kwargs):
        order_id = kwargs['id']
        order = Order.objects.filter(id=order_id).first()

        template_path = 'pdf/sales-invoice.html'
        context = order.generate_invoice_context(request)
        bayer = context['bayer']
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_orderid_{order_id}_user_{bayer}.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


admin.site.register(Order, OrderAdmin)
