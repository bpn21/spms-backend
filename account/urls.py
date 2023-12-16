from django.urls import path, include
from account.views import UserRegistationView, UserLoginView, UserProfileView, UserChangePasswordView, SendResetPasswordEmailView, UserPasswordResetView, VerifyOtpView, SendOtpView
urlpatterns = [
    path('register/', UserRegistationView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('send-otp/', SendOtpView.as_view()),
    path('verify-otp/', VerifyOtpView.as_view()),
    path('userprofile/', UserProfileView.as_view()),
    path('changepassword/', UserChangePasswordView.as_view()),
    path('sendresetpasswordemail/', SendResetPasswordEmailView.as_view()),
    path('resetpassword/<uid>/<token>/', UserPasswordResetView.as_view()),
]
