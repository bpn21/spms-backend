from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class InvoiceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceProduct
        fields = '__all__'

    # def create(self, validated_data):
    #     invoice = self.context['invoice']
    #     return InvoiceProduct.objects.create(invoice=invoice, **validated_data)

class InvoiceSerializer(serializers.ModelSerializer):
    # invoice_products = InvoiceProductSearilizer(many=True)
    class Meta:
        model = Invoice
        fields = '__all__'

    # def create(self, validated_data):
    #     invoice_products_data = validated_data.pop('invoice_products')
    #     invoice = Invoice.objects.create(**validated_data)
    #     for invoice_product_data in invoice_products_data:
    #         serializer = InvoiceProductSearilizer(data=invoice_product_data, context={'invoice': invoice})
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #     return invoice


class SettingsSearilizers(serializers.ModelSerializer):
    class Meta:
        model=Setting
        fields = '__all__'
