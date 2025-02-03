from django.urls import path, include
from .views import (UserRegistrationAPIView,
                    SendOrResendSMSAPIView, UserLoginAPIView, PhoneNumberVerificationAPIView,
                    ResendEmailVerificationView, LogoutView, GoogleLoginView, UserAPIView, ProfileAPIView,
                    AddressAPIView)

# The purpose of defining app_name = 'users' in the urls.py file is to namespace
# the URLs of an app. This helps to uniquely identify and reference the URLs of a specific app,
# especially in projects with multiple apps.
app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user register'),
    path('login/', UserLoginAPIView.as_view(), name="user login"),

    # API endpoint to send an OTP to the registered mobile number
    path('send-sms/', SendOrResendSMSAPIView.as_view(), name="send or resend sms"),

    # API endpoint to verify the phone number by sending an OTP to the registered mobile number and checks the number through and verifies them
    path("verify-phone/", PhoneNumberVerificationAPIView.as_view(),
         name="phone number verification"),

    # API endpoint to resend a verification email inorder to make the email verified for logging in
    path("resend-verification-email/", ResendEmailVerificationView.as_view(),
         name="resend verification email"),

    # API endpoint for log in with google feature
    path("google/login/", GoogleLoginView.as_view(), name="google login"),

    # API endpoint to logout an user by blacklisting the access and refresh tokens
    path("logout/", LogoutView.as_view(), name="logout users"),

    # API endpoint to get the user details
    path("", UserAPIView.as_view(), name="user detail"),

    # API endpoint to get th user profile details
    path("profile/", ProfileAPIView.as_view(), name="user profile info"),

    # API endpoint to get the user profile address info
    path("profile/address/", AddressAPIView.as_view(), name="user address info"),
]
