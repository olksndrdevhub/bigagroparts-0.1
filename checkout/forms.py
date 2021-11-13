from django.forms import ModelForm
from django import forms
from .models import BillingAddress
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _


class BillingForm(ModelForm):
    
    class Meta:
        model = BillingAddress
        fields = ['delivery_method', 'nova_poshta', 'address', 'city', 'landmark', 'phone', 'email', 'payment_method']
        
