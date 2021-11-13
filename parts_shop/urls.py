from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from .views import category_detail, subcategory_detail, item_detail, add_to_card, remove_from_card, remove_single_item_card, edit_account


admin.site.site_header = "BIG AGRO PARTS: панель адміністратора"
admin.site.site_title = "BIG AGRO PARTS: портал адміністратора"
admin.site.index_title = "Ласкаво просимо до адмінпанелі"



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('checkout.urls', namespace='checkout')),
    path('accounts/', include('allauth.urls')),
    path('category/<slug:slug>/', category_detail, name='category_detail'),
    path('subcategory/<slug:slug>/', subcategory_detail, name='subcategory_detail'),
    path('items/<slug:slug>', item_detail,  name='item_detail'),
    path('add-to-card/<slug:slug>/', add_to_card, name='add_to_card'),
    path('remove-from-card/<slug:slug>/',
         remove_from_card, name='remove_from_card'),
    path('remove_single_item_card/<slug:slug>/',
         remove_single_item_card, name='remove_single_item_card'),
    path('', include('core.urls', namespace='core')),
    path('edit/', edit_account, name='edit_account'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls'))
    ]