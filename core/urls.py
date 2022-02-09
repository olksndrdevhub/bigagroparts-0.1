from django.urls import path
from django.conf.urls import url
from .views import HomeView, OrderSummaryView, contacts, conditions, search_view, specorder, my_cabinet, set_language, autocomplete


app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('contacts', contacts, name='contacts_page'),
    path('conditions', conditions, name='conditions_page'),
    path('specorder', specorder, name='specorder'),
    path('search/', search_view, name='search_results'),
    path('my_cabinet', my_cabinet, name='my_cabinet'),
    path('set_language', set_language, name='set_language'),
    url(r'^ajax_calls/search/', autocomplete)
]
