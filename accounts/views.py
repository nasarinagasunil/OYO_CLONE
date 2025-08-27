import random
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Q
from .utils import generateRandomEmailToken, generateSlug, sendEmailToken, sendOTPtoEmail
from accounts.models import Amenities, Hotel, HotelImages, HotelUser, HotelVendor
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

def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)
        hotel_amenities = request.POST.getlist('hotel_amenities')

        hotel_vendor = HotelVendor.objects.get(id=request.user.id)

        hotel = Hotel.objects.create(
            hotel_name=hotel_name,
            hotel_slug=hotel_slug,
            description=hotel_description,
            hotel_price=hotel_price,
            hotel_offer_price=hotel_offer_price,
            hotel_location=hotel_location,
            hotel_owner=hotel_vendor
        )
        for amenity in hotel_amenities:
            amenity = Amenities.objects.get(id=amenity)
            hotel.amenities.add(amenity)
            hotel.save()

        messages.success(request, "Hotel added successfully.")
        return redirect('/account/add_hotel/')

    amenities = Amenities.objects.all()
    return render(request, 'vendor/add_hotel.html', {'amenities': amenities})

@login_required(login_url='login_vendor')
def upload_image(request,hotel_slug):
    hotel = Hotel.objects.get(hotel_slug=hotel_slug)
    if request.method == "POST":
        image=request.FILES.get('image')
        HotelImages.objects.create(
            hotel=hotel,
            image=image
        )
        return HttpResponseRedirect(request.path_info)
    return render(request, 'vendor/upload_image.html', context={'images': hotel.hotel_images.all(), 'hotel': hotel})

@login_required(login_url='login_vendor')
def delete_image(request, id):
    print(id)
    print("#######")
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/account/dashboard/')

@login_required(login_url='login_vendor')
def edit_hotel(request, hotel_slug):
    hotel=Hotel.objects.get(hotel_slug=hotel_slug)
    if request.user.id != hotel.hotel_owner.id:
        return HttpResponse("You are not authorized to edit this hotel.")
    if request.method == "POST":
        # Retrieve updated hotel details from the form
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        
        # Update hotel object with new details
        hotel.hotel_name = hotel_name
        hotel.hotel_description = hotel_description
        hotel.hotel_price = hotel_price
        hotel.hotel_offer_price = hotel_offer_price
        hotel.hotel_location = hotel_location
        hotel.save()
        
        messages.success(request, "Hotel Details Updated")

        return HttpResponseRedirect(request.path_info)

    # Retrieve amenities for rendering in the template
    amenities = Amenities.objects.all()
    return render(request, 'vendor/edit_hotel.html', {'hotel': hotel, 'amenities': amenities})