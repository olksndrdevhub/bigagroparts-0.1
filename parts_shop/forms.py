from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model
from checkout.models import BillingAddress
from phonenumber_field.formfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class MyCustomSignupForm(SignupForm):
    # mail = forms.CharField(required=True, label='Емейл')
    first_name = forms.CharField(required=True, label=_('Ім\'я'))
    last_name = forms.CharField(required=True, label=_('Прізвище'))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        # user.mail = self.cleaned_data['mail']
        user.save()
        return user





class EditUserInfoForm(forms.Form):
    # username = forms.CharField(max_length=100, label=_('Ім\'я користувача'))
    first_name = forms.CharField(max_length=100, label=_('Ім\'я'))
    last_name = forms.CharField(max_length=100, label=_('Прізвище'))
    email = forms.EmailField(label=_('Електронна адреса'))
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': _('+380')}), 
                                    label=_("Номер телефону"), required=False)

    # class Meta:
    #     model = User
    #     fields = ['username', 'first_name', 'last_name', 'email']


class EditBillingAddressForm(forms.ModelForm):
    

    class Meta:
        model = BillingAddress
        fields = ['address', 'nova_poshta', 'city', 'landmark']