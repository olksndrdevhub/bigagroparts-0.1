from django.db import models
from adaptor.model import CsvDbModel

from core.models import Item



class MyCsvModel(CsvDbModel):
    
    class Meta:
        dbModel = Item
        delimiter = ';'