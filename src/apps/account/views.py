# Create your views here.
import os
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from apps.account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from .exceptions import MultileDeviceLoggedIn
import jwt
from django.conf import settings
from apps.account.email import send_otp
from .utils import blacklist_token
from datetime import datetime, timedelta
from apps.account.serializers import (
    UserRegistationSerializer,
    UserLoginSerializer,
    UserProfileViewSerializer,
    UserChangePasswordViewSerializer,
    SendResetPasswordEmailViewSerializer,
)
from apps.account.models import User, OTP, UserToken
from django.utils import timezone


def get_tokens_for_user(refresh):
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistationSerializer(data=request.data)
        device_info = request.META.get("HTTP_USER_AGENT", "") + request.data.get(
            "screen_size"
        )
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            UserToken.objects.create(
                user=user,
                token=token["access"],
                device_info=device_info,
            )

            return Response(
                {
                    "token": token,
                    "msg": "Registration Successful",
                    "status": status.HTTP_201_CREATED,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(email=email, password=password)

            if user is not None:
                tokens = UserToken.objects.filter(user=user)

                if tokens is None and tokens.expiry_time is None:
                    return None

                for token in tokens:
                    if timezone.now() > token.expiry_time:
                        token.delete()

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                decoded_token = jwt.decode(
                    str(access_token), settings.SECRET_KEY, algorithms=["HS256"]
                )
                expiry_time = datetime.fromtimestamp(
                    decoded_token.get("exp"), timezone.utc
                )
                device_info = request.META.get("HTTP_USER_AGENT", "") + str(
                    request.data.get("screen_size")
                )
                userDevice = UserToken.objects.filter(
                    user=user, device_info=device_info
                )

                if userDevice.exists():
                    return Response(
                        {
                            "token": {
                                "refresh": str(refresh),
                                "access": access_token,
                            },
                            "msg": "Login Successful",
                            "status": status.HTTP_200_OK,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    UserToken.objects.create(
                        user=user,
                        token=access_token,
                        device_info=device_info + str(request.data.get("screen_size")),
                        expiry_time=expiry_time,
                    )
                    active_tokens_count = UserToken.objects.filter(user=user).count()

                    if active_tokens_count > 1:
                        oldest_token = (
                            UserToken.objects.filter(user=user)
                            .order_by("created_at")
                            .first()
                        )
                        blacklist_token(oldest_token.token)
                        raise MultileDeviceLoggedIn(
                            f"Otp has been successfully send to {email}",
                            send_otp(email, user)
                            if os.environ.get("DEBUG")
                            else "****",
                            user.id,
                        )

                    return Response(
                        {
                            "token": {
                                "refresh": str(refresh),
                                "access": access_token,
                            },
                            "msg": "Login Successful, New Device Detected !",
                            "status": status.HTTP_200_OK,
                        },
                        status=status.HTTP_200_OK,
                    )

            else:
                return Response(
                    {
                        "error": {
                            "non_field_errors": ["Email or Password is not Valid"]
                        },
                        "status": status.HTTP_404_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileViewSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordViewSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password Changed Succesfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendResetPasswordEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendResetPasswordEmailViewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password reset sent. Please check you email."},
                status=status.HTTP_200_OK,
            )
        else:
            return ValidationError("error")


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = SendResetPasswordEmailViewSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password reset successfully"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOtpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.user.email
        send_otp(email, request)
        return Response(
            {"message": f"Otp has been successfully send to {email}"},
            status=status.HTTP_200_OK,
        )


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.get("otp")
        otp = data.get("otp")
        user_id = data.get("id")
        current_time = timezone.now()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        user_otp = OTP.objects.filter(user_id=user_id).order_by("created_at")
        last_otp = user_otp.last()
        otp_created_at = last_otp.created_at
        time_difference = current_time - otp_created_at
        device_info = request.META.get("HTTP_USER_AGENT", "") + str(
            request.data.get("screen_size")
        )

        if time_difference < timedelta(minutes=30):
            if int(last_otp.otp) == int(otp):
                user.is_varified = True

                active_tokens_count = UserToken.objects.filter(user=user).count()

                if active_tokens_count > 1:
                    oldest_token = (
                        UserToken.objects.filter(user=user)
                        .order_by("created_at")
                        .first()
                    )
                    blacklist_token(oldest_token.token)  # Blacklist the oldest token
                    oldest_token.delete()

                refresh = RefreshToken.for_user(user)
                decoded_token = jwt.decode(
                    str(refresh.access_token), settings.SECRET_KEY, algorithms=["HS256"]
                )
                expiry_time = datetime.fromtimestamp(
                    decoded_token.get("exp"), timezone.utc
                )

                UserToken.objects.create(
                    user=user,
                    token=str(refresh.access_token),
                    device_info=device_info,
                    expiry_time=expiry_time,
                )
                user.save()

                return Response(
                    {
                        "message": "OTP verified successfully.",
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserLogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                {"message": "Authorization header missing or invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header.split()[1]
        user = request.user
        user_token = UserToken.objects.filter(user=user).first()
        if user_token:
            user_token.delete()

        if not user.is_authenticated:
            return Response(
                {"message": "User is not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Try to treat the token as a RefreshToken first
            token_obj = RefreshToken(token)
            token_obj.blacklist()
        except TokenError:
            # If the token is not a RefreshToken, it might be an AccessToken
            try:
                token_obj = AccessToken(token)
                return Response(
                    {"message": "Access token cannot be blacklisted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except TokenError:
                return Response(
                    {"message": "Invalid token type."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user_token = UserToken.objects.filter(user=user).first()
        if user_token:
            user_token.delete()

        return Response(
            {"message": "User logged out successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
