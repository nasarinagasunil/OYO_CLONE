import random
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Q
from .utils import generateRandomEmailToken, sendEmailToken, sendOTPtoEmail
from accounts.models import Hotel, HotelUser, HotelVendor
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
    
def send_otp(request, email):
    hotel_user=HotelUser.objects.filter(email=email)
    if not hotel_user.exists():
        messages.warning(request, "No Account Found.")
        return redirect('/account/login/')
    otp=random.randint(1000,9999)
    hotel_user.update(otp=otp)
    sendOTPtoEmail(email, otp)
    messages.success(request, "An OTP has been sent to your email.")
    return redirect(f'/account/{email}/verify-otp/')

def verify_otp(request, email):
    if request.method == "POST":
        otp=request.POST.get('otp')
        hotel_user = HotelUser.objects.get(email=email)

        if(otp == hotel_user.otp):
            messages.success(request, "OTP verified successfully.")
            return redirect('/account/login/')
        
        messages.warning(request, "Invalid OTP.")
        return redirect(f'/account/login/{email}')
    return render(request, 'verify_otp.html')

def login_vendor(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        hotel_user = HotelVendor.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login_vendor/')

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login_vendor/')

        hotel_user = authenticate(username = hotel_user[0].username , password=password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request , hotel_user)
            return redirect('/account/dashboard/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login_vendor/')
    return render(request, 'vendor/login_vendor.html')

def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number  = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account exists with Email or Phone Number.")
            return redirect('/account/register_vendor/')

        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomEmailToken()
        )
        hotel_user.set_password(password)
        hotel_user.save()

        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register_vendor/')

    return render(request, 'vendor/register_vendor.html')

@login_required(login_url='login_vendor')
def dashboard(request):
    # Retrieve hotels owned by the current vendor
    hotels = Hotel.objects.filter(hotel_owner=request.user)
    context = {'hotels': hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)