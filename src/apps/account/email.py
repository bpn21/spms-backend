from django.core.mail import send_mail
from django.conf import settings
import random
from apps.account.models import User, OTP


def send_otp(email, user):
    otp = random.randint(1000, 9999)
    OTP.objects.create(user=user, otp=otp)
    otp = OTP.objects.filter(user=user).last()
    otp = otp.otp
    user.otp = otp
    user.save()
    subject = "Sita Sweet Home Production"
    message = f"Your otp is {otp}. Do not share this otp with anyone1. \n Kinds regards\n Sita Sweet Home Production.\n"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
