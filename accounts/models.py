from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class HotelUser(User):
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    phone_number = models.CharField(max_length=15, unique=True)
    email_token = models.CharField(max_length=100, blank=True, null=True)
    otp = models.CharField(max_length=10, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    class Meta:
        db_table = 'hotel_user'

class HotelVendor(User):
    profile_picture = models.ImageField(upload_to='vendor_profile_pictures/')
    phone_number = models.CharField(max_length=15, unique=True)
    business_name = models.CharField(max_length=200)
    email_token = models.CharField(max_length=100, blank=True, null=True)
    otp = models.CharField(max_length=10, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'hotel_vendor'

class Amenities(models.Model):
    name = models.CharField(max_length=1000)
    icon = models.ImageField(upload_to='amenities_icons/')
    def __str__(self) -> str:
        return self.name

class Hotel(models.Model):
    hotel_name = models.CharField(max_length=200)
    description = models.TextField()
    hotel_slug = models.SlugField(max_length=100,unique=True)
    hotel_owner = models.ForeignKey(HotelVendor, on_delete=models.CASCADE, related_name='hotels')
    amenities = models.ManyToManyField(Amenities)
    hotel_price = models.FloatField()
    hotel_offer_price = models.FloatField()
    hotel_location = models.TextField()
    is_active = models.BooleanField(default=False)

class HotelImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_images')
    image = models.ImageField(upload_to='hotel_images/')

class HotelManager(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='managers')
    manager_name = models.CharField(max_length=100)
    manager_contact = models.CharField(max_length=15)