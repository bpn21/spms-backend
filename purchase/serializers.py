from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model= Products
        fields='__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Purchase
        fields= '__all__'

