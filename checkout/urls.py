from django.urls import path
from .views import checkout, generate_invoice_in_cabinet

app_name = 'checkout'

urlpatterns = [
    path('checkout/', checkout, name='index'),
    path('<int:order_code>/generate_invoice_in_cabinet/', generate_invoice_in_cabinet, name='generate_invoice_in_cabinet'),
    # path('checkout_success/', checkout_success, name='checkout_success'),
]
