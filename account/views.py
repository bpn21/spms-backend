# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
import jwt
from django.conf import settings
from account.email import send_otp
from .utils import blacklist_token

from datetime import datetime, timedelta
from account.serializers import (
    UserRegistationSerializer,
    UserLoginSerializer,
    UserProfileViewSerializer,
    UserChangePasswordViewSerializer,
    SendResetPasswordEmailViewSerializer,
)
from account.models import User, OTP, UserToken
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
        if serializer.is_valid():
            user = serializer.save()  # Save the new user
            token = get_tokens_for_user(user)  # Generate tokens for the new user

            # Create the initial token record
            UserToken.objects.create(
                user=user,
                token=token["access"],  # Store the access token
                device_info=request.META.get(
                    "HTTP_USER_AGENT", ""
                ),  # Store device info if needed
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
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(email=email, password=password)

            if user is not None:
                tokens = UserToken.objects.filter(user=user)

                # Delete expired tokens
                for token in tokens:
                    if timezone.now() > token.expiry_time:
                        token.delete()
                active_tokens_count = UserToken.objects.filter(user=user).count()

                refresh = RefreshToken.for_user(user)
                if active_tokens_count >= 1:
                    send_otp(email, user)
                    raise ValidationError(
                        {
                            "message": f"Otp has been successfully send to {email}",
                            "status": status.HTTP_403_FORBIDDEN,
                            "token": {
                                "refresh": str(refresh),
                                "access": str(refresh.access_token),
                            },
                        },
                    )

                decoded_token = jwt.decode(
                    str(refresh.access_token), settings.SECRET_KEY, algorithms=["HS256"]
                )
                expiry_time = datetime.fromtimestamp(
                    decoded_token.get("exp"), timezone.utc
                )

                UserToken.objects.create(
                    user=user,
                    token=str(refresh.access_token),
                    device_info=request.META.get("HTTP_USER_AGENT", ""),
                    expiry_time=expiry_time,
                )
                return Response(
                    {
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                        "msg": "Login Successful",
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
    # To handel Errors
    renderer_classes = [UserRenderer]

    # To remove AnonymousUser
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileViewSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]

    # To avoid AnonymousUser, only authenticated user can access.
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.user.email
        otp = request.data["otp"]
        current_time = datetime.now()
        # 2023-12-16 17:12:34.445411 current time<<<<<<<<<<<<<
        # 2023-12-16 16:53:47.880 +0545 created time >>>>>> As there is "+0545". This is timezone-aware datetime object
        # In absence of "+0545". we need to make aware about timezone ,

        # syntax: timezone.make_aware(date)
        # 362.26969913333335 time difference.....
        # why?
        # To handle this situation correctly, you should ensure that both timestamps are in the same timezone before calculating the time difference. If your Django project is configured to use the 'Asia/Kathmandu' timezone, you can convert the current_time to this timezone:

        # Convert current_time to the timezone used in your database (e.g., 'Asia/Kathmandu')
        # USE ANY ONE
        # current_time = current_time.astimezone(timezone.get_current_timezone())
        # OR
        current_time = timezone.make_aware(current_time)

        user_otp = OTP.objects.filter(user_id=request.user.id)
        last_otp = user_otp.last()
        otp_created_at = last_otp.created_at
        time_difference = current_time - otp_created_at

        if time_difference < timedelta(minutes=5):
            if int(last_otp.otp) == int(otp):
                request.user.is_varified = True
                request.user.save()
                return Response(
                    {"message": "Email has been verified"}, status=status.HTTP_200_OK
                )
            else:
                return Response({"message": "OTP did not match."})
        else:
            return Response({"message": "OTP has been expired."})


class UserLogoutView(APIView):
    def post(self, request):
        user = request.user
        if not request.user.is_authenticated:
            return Response(
                {"message": "User is not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_token = UserToken.objects.filter(user=user).first()
        print(user_token, "TOKEN IS HERE")
        if user_token:
            user_token.delete()

        return Response(
            {"msg": "Logout Successful", "status": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )
