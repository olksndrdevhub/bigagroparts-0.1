from django.forms import ModelForm
from .models import Order
from django.utils.translation import gettext_lazy as _


class BillingForm(ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_method', 'nova_poshta', 'customer_name', 'address', 'city', 'landmark', 'phone', 'email', 'payment_method']
