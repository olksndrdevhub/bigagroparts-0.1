import locale
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

from core.models import Item, Order


User = get_user_model()


class BillingAddress(models.Model):

    NOVA_POSHTA = 'NP'
    KURIER = 'KU'
    DELIVERY_METHODS = (
        (NOVA_POSHTA, _('Нова Пошта')),
        (KURIER, _("Кур'єр (по м. Луцьк)"))
    )
    PAY_AFTER_DELIVERING = 'PAD'
    PAY_BEFORE_DELIVERING = 'PBD'
    PAYMENT_METHODS = (
        (PAY_AFTER_DELIVERING, _('Оплата при отриманні')),
        (PAY_BEFORE_DELIVERING, _('Оплата за реквізитами (передоплата)'))
    )

    total_price = models.CharField(verbose_name=_('Сума замовлення'), max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Замовлення')
    delivery_method = models.CharField(verbose_name=_('Метод доставки:'), choices=DELIVERY_METHODS, max_length=5, default=NOVA_POSHTA)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nova_poshta = models.CharField(max_length=5, verbose_name=_('№ відділення Нової Пошти'), help_text=_("Введіть лише число без '№'"), blank=True)
    city = models.CharField(max_length=100, verbose_name=_('Місто / село'), blank=True)
    address = models.CharField(max_length=200, verbose_name=_('Адреса для доставки по Луцьку'), blank=True)
    landmark = models.CharField(max_length=100, verbose_name=_('Область'), blank=True)
    phone = PhoneNumberField(verbose_name=_('Контактний номер телефону'))
    email = models.EmailField(verbose_name=_('Адреса електронної пошти'), max_length=200)
    payment_method = models.CharField(verbose_name=_('Метод оплати'), choices=PAYMENT_METHODS, max_length=10, default=PAY_BEFORE_DELIVERING)

    def generate_invoice_context(self, request):

        locale.setlocale(locale.LC_ALL, 'uk_UA.utf8')
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        context = {
            'deliver': request.get_host(),
            'bayer': self.user.first_name + ' ' + self.user.last_name,
            'bayer_info': self.delivery_method,
            'time': dt_string,
            'order': self.order,
            'order_items': self.order.items.all(),
            'order_code': self.order.id,
            'order_total': self.total_price,
            'item_count': len(self.order.items.all()),
        }
        return context

    def __str__(self):
        return f'{self.user.email} order'

    class Meta:
        verbose_name_plural = 'Інформація про замовлення'
