from django.urls import path, include
from .views import *

urlpatterns = [
    path('clients/', ClientView.as_view()),
    path('client/<int:pk>/', ClientView.as_view()),
    path('employee/', EmployeeView.as_view()),
    path('employee/<int:pk>/', EmployeeView.as_view()),
]
