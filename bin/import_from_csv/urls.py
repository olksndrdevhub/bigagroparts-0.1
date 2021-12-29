from django.urls import path
from .views import import_from_csv

app_name = 'import_from_csv'

urlpatterns = [
    path('/csv/import_from', import_from_csv, name='import_from_csv')
]
