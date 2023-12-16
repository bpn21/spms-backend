from django.core.mail import send_mail
from django.conf import settings
import random
from account.models import User, OTP


def send_otp(email, request):
    otp = random.randint(1000,9999)
    OTP.objects.create(user=request.user, otp=otp)
    otp = OTP.objects.filter(user=request.user).last()
    otp = otp.otp
    request.user.otp = otp
    request.user.save()
    subject = 'Sita Sweet Home Production'
    message = f'Your otp is {otp}. Do not share this otp with anyone1. \n Kinds regards\n Sita Sweet Home Production.\n'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
