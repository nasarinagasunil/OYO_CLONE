import uuid
from django.core.mail import send_mail
from django.conf import settings

from accounts.models import Hotel
from django.utils.text import slugify
def generateRandomEmailToken():
    return str(uuid.uuid4())

def sendEmailToken(email, token):
    subject = "Verify your email"
    message = f"""Hi, Verify your email with the following link: 

        http://127.0.0.1:8000/account/view_account/{token}/

    """
    send_mail(
        subject, 
        message, 
        settings.EMAIL_HOST_USER,  # From email
        [email],                # To email (list)
        )
    
def sendOTPtoEmail(email,otp):
    subject = "OTP for Account login"
    message = f"""Hi, Your OTP for login is: 

                {otp}

    """
    send_mail(
        subject, 
        message, 
        settings.EMAIL_HOST_USER,  # From email
        [email],                # To email (list)
    )

def generateSlug(hotel_name):
    slug = f"{slugify(hotel_name)}-" + str(uuid.uuid4()).split('-')[0]
    if Hotel.objects.filter(hotel_slug = slug).exists():
        return generateSlug(hotel_name)
    return slug