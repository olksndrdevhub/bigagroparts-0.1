from django.shortcuts import render

from .models import MyCsvModel

def import_from_csv(request):
    my_csv_list = MyCsvModel.import_data(data = open('/csv_uploaded/items.csv'))
    first_line = my_csv_list[0]
    print(first_line.title)
    
    return render(request, 'import_from_csv.html', context={'first_line': first_line})