from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from .utils import generateRandomEmailToken, sendEmailToken
from accounts.models import HotelUser
# Create your views here.
def login_page(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelUser.objects.filter(email=email)

        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login/')

        user = authenticate(request, username=hotel_user[0].username, password=password)

        if user:
            messages.success(request, "Login Success")
            login(request, user)
            return redirect('/account/login/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login/')
    return render(request, 'login.html')

def register(request):
    if(request.method == "POST"):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user=HotelUser.objects.filter(Q(email=email) | Q(phone_number=phone_number))
        if hotel_user.exists():
            messages.error(request, "User with this email and phone number already exists.")
            return redirect('register')
        hotel_user=HotelUser.objects.create(
            username=phone_number,
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            email_token=generateRandomEmailToken(),
            phone_number=phone_number
        )
        hotel_user.set_password(password)
        hotel_user.save()
        sendEmailToken(email, hotel_user.email_token)
        messages.success(request, "An email is sent to your email address for verification.")
        return redirect('register')
    return render(request, 'register.html')

def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token=token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Your email has been verified successfully.")
        return redirect('login')
    except HotelUser.DoesNotExist:
        return HttpResponse("Invalid token")