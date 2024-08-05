from django.urls import path, include
from account.views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserChangePasswordView,
    SendResetPasswordEmailView,
    UserPasswordResetView,
    VerifyOtpView,
    SendOtpView,
    UserLogoutView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("logout/", UserLogoutView.as_view()),
    path("send-otp/", SendOtpView.as_view()),
    path("verify-otp/", VerifyOtpView.as_view()),
    path("userprofile/", UserProfileView.as_view()),
    path("changepassword/", UserChangePasswordView.as_view()),
    path("sendresetpasswordemail/", SendResetPasswordEmailView.as_view()),
    path("resetpassword/<uid>/<token>/", UserPasswordResetView.as_view()),
]
