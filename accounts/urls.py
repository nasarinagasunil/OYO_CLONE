
from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    path('view_account/<str:token>/', views.verify_email_token, name='verify_email_token'),
]