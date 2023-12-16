# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from account.email import send_otp
from datetime import datetime, timedelta
from account.serializers import UserRegistationSerializer, UserLoginSerializer, UserProfileViewSerializer, UserChangePasswordViewSerializer, SendResetPasswordEmailViewSerializer
from account.models import User, OTP
from django.utils import timezone



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistationView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({
                'token': token,
                'msg': 'Registation Success',
                'status': status.HTTP_201_CREATED,
            }, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        """When a client sends a POST request to this view,
        the UserLoginSerializer is used to deserialize the request data into a Python dictionary,
         which is then passed to the data parameter of the serializer."""
        if serializer.is_valid(raise_exception=True):
            """. If the data is valid, the is_valid() method returns True.
            Otherwise, it raises a serializers.ValidationError exception."""
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            """If the data is valid, the email and password values are extracted from the serializer.data dictionary,
            and the authenticate() method is called with these values to check
            if there is a user in the database with the given email and password."""
            if user is not None:
                token = get_tokens_for_user(user)
                """If the authenticate() method returns a user object,
                it means the user's email and password are valid,
                and a success response is returned with status code 200 and
                a message indicating that the login was successful."""
                return Response({
                    'token': token,
                    'msg': "Login Successfull",
                    'status': status.HTTP_200_OK
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': {'non_fields_errors': ['Email or Password is not Valid']},
                    'status': status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)


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
            data=request.data, context={'user': request.user})
        if(serializer.is_valid(raise_exception=True)):
            return Response({'msg': 'Password Changed Succesfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendResetPasswordEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendResetPasswordEmailViewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password reset sent. Please check you email.'}, status=status.HTTP_200_OK)
        else:
            return ValidationError('error')


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = SendResetPasswordEmailViewSerializer(
            data=request.data, context={"uid": uid, "token": token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': "Password reset successfully"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOtpView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.user.email
        send_otp(email, request)
        return Response({"message": f'Otp has been successfully send to {email}'},status=status.HTTP_200_OK)
        

class VerifyOtpView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.user.email
        otp = request.data['otp']
        current_time = datetime.now()
        print(current_time, 'current time')
        #2023-12-16 17:12:34.445411 current time<<<<<<<<<<<<<
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

        print(time_difference.total_seconds()/60,'time difference????')
        if time_difference < timedelta(minutes=5):
            if int(last_otp.otp) == int(otp):
                request.user.is_varified = True
                request.user.save()
                return Response({"message": 'Email has been verified'}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"OTP did not match."})
        else:
                return Response({"message":"OTP has been expired."})
