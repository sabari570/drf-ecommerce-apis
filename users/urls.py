from django.urls import path, include
from .views import (UserRegistrationAPIView,
                    SendOrResendSMSAPIView, UserLoginAPIView)

# The purpose of defining app_name = 'users' in the urls.py file is to namespace
# the URLs of an app. This helps to uniquely identify and reference the URLs of a specific app,
# especially in projects with multiple apps.
app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user register'),
    path('login/', UserLoginAPIView.as_view(), name="user login"),
    path('send-sms/', SendOrResendSMSAPIView.as_view(), name="send or resend sms"),
]
