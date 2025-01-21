from django.urls import path 
from .views import  LogoutView, EmailValidationView, LoginView
from django.views.decorators.csrf import csrf_exempt
from .views import ClientLoginView
urlpatterns = [
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()),
         name='validate_email'),
    path('loginClient/', ClientLoginView.as_view(), name='login'),
    
]
