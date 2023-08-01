from django.urls import path, include
from .views import *
from django.contrib import admin


urlpatterns = [
    path('products/', ProductView.as_view()),
    path('products/<int:pk>', ProductView.as_view()),
    path('invoice/', InvoiceAPIView.as_view()),
    path('invoice/<int:pk>/', InvoiceAPIView.as_view()),
    # path('csi/', ClientSalesInformationView.as_view()),
]
