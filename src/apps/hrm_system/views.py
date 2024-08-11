from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from apps.hrm_system.serializers import ClientSerializer
from apps.hrm_system.serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from apps.hrm_system.models import Client


# Create your views here.
class ClientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                unit = Client.objects.get(id=pk, user=request.user)
                serializer = ClientSerializer(unit)
            except Client.DoesNotExist:
                return Response(
                    {
                        "error": True,
                        "data": "No Client found",
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            unit = Client.objects.filter(user=request.user)
            serializer = ClientSerializer(unit, many=True)
        return Response(
            {"error": False, "data": serializer.data, "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ClientSerializer(data=request.data, many=True)
        # json format is now converted to table query set.

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {
                    "error": False,
                    "data": "Client has been Added.",
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

    def patch(self, request):
        try:
            try:
                id = request.data["client_id"]
            except:
                return Response({"data": "client_id must be sent to update"})
            unit = Client.objects.get(id=id, user=request.user)
            serializer = ClientSerializer(unit, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(
                    {
                        "error": False,
                        "data": "Client has been updated.",
                        "status": status.HTTP_201_CREATED,
                    },
                    status=status.HTTP_201_CREATED,
                )
        except:
            return Response(
                {
                    "error": True,
                    "data": f"Client not found with unit_id {id} ",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request):
        try:
            id = request.data["unit_id"]
            unit = Client.objects.get(id=id, user=request.user)
            unit.delete()
            return Response(
                {
                    "error": False,
                    "data": "Client has been deleted.",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except Client.DoesNotExist:
            return Response(
                {
                    "error": True,
                    "data": f"Client not found with unit_id {id} ",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class EmployeeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            try:
                units = Employee.objects.get(id=pk, user=request.user)
                serializer = EmployeeSerializer(units)
            except Employee.DoesNotExist:
                return Response(
                    {
                        "error": True,
                        "data": f"Employee with id {pk} does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            except ValidationError as e:
                return Response(
                    {
                        "error": True,
                        "data": e.detail,
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response({"error": False, "data": serializer.data})
        else:
            try:
                units = Employee.objects.filter(user=request.user)
                serializer = EmployeeSerializer(units, many=True)
                return Response(
                    {
                        "error": False,
                        "data": serializer.data,
                        "status": status.HTTP_200_OK,
                    },
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "error": True,
                        "data": "Employee not found.",
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data, many=True)
        if isinstance(request.data, list):
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(
                    {
                        "error": False,
                        "data": f"Employee has been Added.{serializer.data}",
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
        else:
            return Response(
                {
                    "error": True,
                    "data": "Expected a list but got object",
                    "status": status.HTTP_400_BAD_REQUEST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def patch(self, request):
        try:
            id = request.data["unit_id"]
            unit = Employee.objects.get(id=id)
            serializer = EmployeeSerializer(unit, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "error": False,
                        "data": "Employee has been updated.",
                        "status": status.HTTP_201_CREATED,
                    },
                    status=status.HTTP_201_CREATED,
                )
        except:
            return Response(
                {
                    "error": True,
                    "data": "Employee not found.",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request):
        try:
            id = request.data["unit_id"]
            unit = Employee.objects.get(id=id)
            unit.delete()
            return Response(
                {
                    "error": False,
                    "data": "Employee has been deleted.",
                    "status": status.HTTP_200_OK,
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {
                    "error": True,
                    "data": "Employee not found.",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
