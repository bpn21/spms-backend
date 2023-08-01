from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register((Product,Client,Employee,License,Citizenship,Bill,ClientSalesInformation,SalesItem))
admin.site.register((Product,Invoice,Setting))
