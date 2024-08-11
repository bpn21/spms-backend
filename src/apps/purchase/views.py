from django.shortcuts import render
from apps.purchase import serializers
from apps.purchase.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            product = Products.objects.filter(user=request.user)
            serializer = ProductSerializer(product, many=True)
            return Response(
                {"error": False, "data": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            try:
                product = Products.objects.get(user=request.user, id=pk)
                serializer = ProductSerializer(product, many=True)
                return Response(
                    {
                        "error": False,
                        "data": serializer.data,
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            except:
                return Response(
                    {
                        "error": True,
                        "data": "Product Not Found",
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

    def post(self, request):
        token = request.headers.get("Authorization")

        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {
                "error": False,
                "data": "Product has been added",
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            purchase = Purchase.objects.filter(user=request.user)
            serializer = PurchaseSerializer(purchase, many=True)
            return Response(
                {"error": False, "data": serializer.data, "status": status.HTTP_200_OK},
                status=status.HTTP_200_OK,
            )
        else:
            try:
                purchase = Purchase.objects.get(user=request.user, id=pk)
                serializer = PurchaseSerializer(purchase, many=True)
                return Response(
                    {
                        "error": False,
                        "data": serializer.data,
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            except:
                return Response(
                    {
                        "error": True,
                        "data": "Purchase Not Found",
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
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
        return Response(
            {
                "error": True,
                "data": serializer.errors,
                "status": status.HTTP_400_BAD_REQUEST,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
