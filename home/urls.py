from django.urls import path

from home.views import hotel_details, index

urlpatterns = [
    path('', index, name='index'),
    path('hotel_details/<slug:hotel_slug>/', hotel_details, name='hotel_details'),

]