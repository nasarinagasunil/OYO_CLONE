
from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    path('send-otp/<str:email>/', views.send_otp, name='send_otp'),
    path('<str:email>/verify-otp/', views.verify_otp, name='verify_otp'),
    path('view_account/<str:token>/', views.verify_email_token, name='verify_email_token'),
    path('login_vendor/', views.login_vendor, name='login_vendor'),
    path('register_vendor/', views.register_vendor, name='register_vendor'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_hotel/', views.add_hotel, name='add_hotel'),
    path('upload_image/<slug:hotel_slug>/', views.upload_image, name='upload_image'),
    path('delete_image/<id>/', views.delete_image, name='delete_image'),
    path('edit_hotel/<slug:hotel_slug>/', views.edit_hotel, name='edit_hotel'),
    path('logout/' , views.logout_view , name="logout_view"),
]