from django.urls import path,include
from .views import *
from django.contrib import admin

urlpatterns = [
    path('product/', ProductView.as_view()),
    # path('product/<int:pk>', ProductView.as_view()),
    path('purchase/',PurchaseView.as_view()),
    # path('purchase/<int:pk>/', PurchaseView.as_view()),
    # path('csi/', ClientSalesInformationView.as_view()),
]