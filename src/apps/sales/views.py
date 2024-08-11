from .serializers import *

# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
import jwt
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
import pytz
from apps.hrm_system import serializers
from apps.hrm_system.serializers import *

# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            units = Product.objects.filter(user=request.user)
            if units:
                serializer = ProductSerializer(units, many=True)
                return Response(
                    {
                        "error": False,
                        "data": serializer.data,
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "error": True,
                        "data": "Product Not Found",
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # except:
            #     return Response({
            #         "error": True,
            #         "data": "Product Not Found",
            #         "status": status.HTTP_404_NOT_FOUND
            #     }, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                unit = Product.objects.get(id=pk)
                if unit.user == request.user:
                    serializer = ProductSerializer(unit)
                    return Response(
                        {
                            "error": False,
                            "data": serializer.data,
                            "status": status.HTTP_200_OK,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    # Raised NotFound exception for unauthorized access to a product
                    raise NotFound("Product Not Found")
            except Product.DoesNotExist:
                # Raised NotFound exception when the product does not exist
                raise NotFound("Product Not Found")

    def post(self, request):
        serializer = ProductSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {
                    "error": False,
                    "data": "Product has been created.",
                    "status": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
            )
        print(serializer.errors, "err is here")
        return Response(
            {
                "error": True,
                "data": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request):
        try:
            id = request.data["item_id"]
            unit = Product.objects.get(id=id)
            serializer = ItemSerializer(unit, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "error": False,
                        "data": "Product has been updated.",
                        "status": status.HTTP_201_CREATED,
                    },
                    status=status.HTTP_201_CREATED,
                )
        except:
            return Response(
                {
                    "error": True,
                    "data": "Product not found.",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request):
        try:
            id = request.data["item_id"]
            unit = Product.objects.get(id=id)
            unit.delete()
            return Response(
                {
                    "error": False,
                    "data": "Product has been deleted.",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {
                    "error": True,
                    "data": "Product not found.",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class InvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self,request):
    # invoice_units = Invoice.objects.all()
    #     serializer = InvoiceSerializer(invoice_units,many=True)

    # units = InvoiceProduct.objects.all()
    #     invoice_product_serializer = InvoiceProductSerializer(units,many=True)
    #     invoice_product_serialized_data = invoice_product_serializer.data

    #     total_invoice = []
    #     for item in invoice_units_serialized_data:
    #         invoice = {}
    #         matching_products = filter(lambda p: p.get('invoice')==item['id'],invoice_product_serialized_data)
    #         matching_products_list = list(matching_products)
    #         invoice['product'] = matching_products_list

    #         # invoice['invoice'] = item
    #         for invoice_item in item:
    #             invoice[invoice_item] = item[invoice_item]
    #         total_invoice.append(invoice)
    #     return Response({
    #         "error":False,
    #         "data":serializer.data,
    #         "status":status.HTTP_200_OK
    #     },status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if "products" in request.data and isinstance(request.data["products"], list):
            for product_data in request.data["products"]:
                if (
                    "product" in product_data
                    and "quantity" in product_data
                    and "price" in product_data
                ):
                    if isinstance(product_data["product"], (int, float)) and isinstance(
                        product_data["quantity"], (int, float)
                    ):
                        if product_data["product"] > 0 and product_data["quantity"] > 0:
                            serializer = InvoiceSerializer(data=request.data)
                            serializer.is_valid(raise_exception=True)
                            # Save the invoice instance
                            invoice = serializer.save(user=request.user)
                            # Loop through the invoice products and create them
                            try:
                                for product_data in request.data.get("products", []):
                                    # Add the invoice foreign key to the product data
                                    updated_product_data = dict(product_data)
                                    updated_product_data["invoice"] = invoice.pk
                                    # Serialize the product data and create the product instance
                                    product_serializer = InvoiceProductSerializer(
                                        data=updated_product_data
                                    )
                                    product_serializer.is_valid(raise_exception=True)
                                    product_serializer.save(user=request.user)
                                # Serialize the invoice instance and return it in the response
                                serialized_invoice = InvoiceSerializer(invoice)
                                return Response(
                                    {"data": "invoice has been created"},
                                    status=status.HTTP_201_CREATED,
                                )
                            except ValidationError as e:
                                invoice.delete()
                                return Response(
                                    {"error": e.detail},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                        else:
                            raise serializers.ValidationError(
                                "product, amout and price must be greater than zero"
                            )
                    else:
                        # Handle missing or invalid data
                        # return Response({'error':'product and quantity is required'},status= status.HTTP_400_BAD_REQUEST)
                        # raise serializers.ValidationError("Product, price and number must be number.")
                        return Response(
                            {"message": "Product, price and number must be number."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                else:
                    # Handle missing or invalid data
                    return Response(
                        {"error": "product, quantity and price is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        else:
            # Handle missing or invalid data
            print("i am here")
            return Response(
                {"error": "No products found"}, status=status.HTTP_400_BAD_REQUEST
            )

    def get_invoice(self, type, pk=None):
        try:
            print("bipins pk", pk)
            if type == "patch":
                return Invoice.objects.get(bill_number=pk)
            else:
                return Invoice.objects.filter(bill_number=pk)
        except Invoice.DoesNotExist:
            print("not found")
            raise

    def get_invoice_product(self, invoice):
        try:
            return InvoiceProduct.objects.filter(invoice=invoice)
        except Invoice.DoesNotExist:
            print("invoice product")
            raise

    def get(self, request, pk=None):
        if pk is not None:
            invoice = self.get_invoice(request, "get", pk)

            invoice_serializer = InvoiceSerializer(invoice)
            InvoiceProduct = self.get_invoice_product(invoice_serializer.data["id"])
            invoice_product_serializer = InvoiceProductSerializer(
                InvoiceProduct, many=True
            )
            data = {
                "id": invoice.id,
                "due_date": invoice.due_date,
                "remarks": invoice.remarks,
                "payment_terms": invoice.payment_terms,
                "payment_status": invoice.payment_status,
                "bill_number": invoice.bill_number,
                "client": ClientSerializer(invoice.client).data["client_name"],
                "employee": EmployeeSerializer(invoice.employee).data["full_name"],
                "products": invoice_product_serializer.data,
            }
        else:
            invoices = Invoice.objects.filter(user=request.user)
            data = []
            for invoice in invoices:
                invoice_serializer = InvoiceSerializer(invoice)
                invoice_products = self.get_invoice_product(invoice)
                invoice_product_serializer = InvoiceProductSerializer(
                    invoice_products, many=True
                )
                data.append(
                    {
                        "id": invoice.id,
                        "due_date": invoice.due_date,
                        "remarks": invoice.remarks,
                        "payment_terms": invoice.payment_terms,
                        "payment_status": invoice.payment_status,
                        "bill_number": invoice.bill_number,
                        "client": ClientSerializer(invoice.client).data["client_name"],
                        "employee": EmployeeSerializer(invoice.employee).data[
                            "full_name"
                        ],
                        "products": invoice_product_serializer.data,
                    }
                )
        return Response(data)

    def patch(self, request, pk=None):
        invoice = self.get_invoice("patch", pk)
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            invoice.products.all().delete()
            products_data = request.data.get("products")
            if products_data:
                for product_data in products_data:
                    product_data["invoice"] = invoice.pk
                invoice_product_serializer = InvoiceProductSerializer(
                    data=products_data, many=True
                )
                if invoice_product_serializer.is_valid():
                    invoice_product_serializer.save()
                else:
                    return Response(
                        invoice_product_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response({"data": serializer.data, "status": status.HTTP_200_OK})
        else:
            print("not valid")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
