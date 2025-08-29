from django.shortcuts import render
from accounts.models import Hotel

# Create your views here.
def index(request):
    hotels=Hotel.objects.all()
    if request.GET.get('search'):
        hotels=Hotel.objects.filter(hotel_name__icontains=request.GET.get('search'))
    if request.GET.get('sort_by'):
        sort_by=request.GET.get('sort_by')
        if sort_by=="sort_low":
            hotels=hotels.order_by('hotel_price')
        elif sort_by=="sort_high":
            hotels=hotels.order_by('-hotel_price')

    return render(request, 'index.html', {'hotels': hotels})

def hotel_details(request, hotel_slug):
    hotel = Hotel.objects.get(hotel_slug = hotel_slug)
    return render(request, 'hotel_details.html', context = {'hotel' : hotel})


