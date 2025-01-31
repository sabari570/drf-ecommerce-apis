from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from .serializers import (UserRegistrationSerializer, PhoneNumberSerializer,
                          UserLoginSerializer, PhoneNumberVerificationSerializer)
from .utils import send_or_resend_sms
from rest_framework.exceptions import APIException
from .exceptions import InternalServerErrorException, TokenBlackListedException
# this is for including transactions in our API while interacting with DB
from django.db import transaction
from allauth.account.utils import send_email_confirmation
from dj_rest_auth.registration.serializers import ResendEmailVerificationSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils.timezone import datetime, make_aware
from decouple import config

# Imports for google login setup
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView

# Create your views here.

User = get_user_model()


class UserRegistrationAPIView(RegisterView):
    '''
    Register new users using phone number or email and password
    '''
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Code for wrapping everything in a single transaction
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                # User model is created inside perform_create() in RegisterView
                # and the EmailAddresses model is also getting filled automatically when the user record is created by the RegisterView
                user = self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)

                response_data = ''
                email = request.data.get('email', None)
                phone_number = request.data.get('phone_number', None)

                if email and phone_number:
                    otp = send_or_resend_sms(phone_number)
                    response_data = {
                        "detail": "Verification e-mail and SMS sent successfully.",
                        "secuity code": str(otp),
                    }
                elif email and not phone_number:
                    # This sends a verification email to the registered user
                    send_email_confirmation(request, user)
                    response_data = {"detail": _("Verification e-mail sent")}
                else:
                    otp = send_or_resend_sms(phone_number)
                    response_data = {
                        "detail": "Verification SMS sent successfully.",
                        "secuity code": str(otp),
                    }
                return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        except APIException as e:
            raise e
        except Exception as e:
            print("Exception while registering user: ", str(e))
            raise InternalServerErrorException()


class SendOrResendSMSAPIView(GenericAPIView):
    serializer_class = PhoneNumberSerializer

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    # Convert the validated phone number to string
                    phone_number = str(
                        serializer.validated_data["phone_number"])
                    otp = send_or_resend_sms(phone_number)
                    if not otp:
                        return Response({"error": "Phone number not found or already verified."}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({"message": "SMS verification code sent successfully.", "otp": otp}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except APIException as e:
            raise e
        except Exception as e:
            print("Exception while sending OTP to user: ", str(e))
            raise InternalServerErrorException()

# This class is the UserLoginview that inherits the LoginView from the serializer


class UserLoginAPIView(LoginView):
    '''
    Authenticate existing users using email or phone and password
    '''
    serializer_class = UserLoginSerializer


class PhoneNumberVerificationAPIView(GenericAPIView):
    '''
    This view is used to verify the phone number with its secure OTP generated
    '''
    serializer_class = PhoneNumberVerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    message = {"detail": _(
                        "Your phone number is verified successfully")}
                    return Response(message, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except APIException as e:
            raise e
        except Exception as e:
            print(f"Error while verifying the phone number with OTP: ", str(e))
            raise InternalServerErrorException()

# Custom view for Resend email verification


class ResendEmailVerificationView(GenericAPIView):
    '''
    This view is used to resend the verification emails to those that are not verified
    '''
    serializer_class = ResendEmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.filter(
                email=serializer.validated_data["email"]).first()
            if not user:
                return Response({'mesage': _('This user is not registered')}, status=status.HTTP_400_BAD_REQUEST)
            email = user.emailaddress_set.filter(email=user.email).first()
            if email and not email.verified:
                send_email_confirmation(request, user)
                return Response({'detail': _('ok')}, status=status.HTTP_200_OK)
            else:
                return Response({'mesage': _('Email not registered or it is already verified')}, status=status.HTTP_400_BAD_REQUEST)
        except APIException as e:
            raise e
        except Exception as e:
            print(e)
            raise InternalServerErrorException()


class LogoutView(GenericAPIView):
    '''
    Custom Logout view that deletes the cookies and invalidas them by adding the tokens to Blacklisted tokens.
    '''
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            ACCESS_TOKEN_COOKIE_KEY = getattr(
                settings, 'JWT_AUTH_COOKIE', None)
            REFRESH_TOKEN_COOKIE_KEY = getattr(
                settings, 'JWT_AUTH_REFRESH_COOKIE', None)

            refresh_token = request.COOKIES.get(
                REFRESH_TOKEN_COOKIE_KEY)    # Get access token from cookies
            # Get refresh token from cookies
            access_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_KEY)

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()   # Blacklisting the refresh token

            # Blacklist the access token by finding the corresponding OutStandingToken.
            # Inorder to solve the "BlacklistedToken.token" must be a "OutstandingToken" instance." issue
            if access_token:
                token = AccessToken(access_token)

                # Get the JWT ID (jti)
                jti = token['jti']
                exp_timestamp = token['exp']
                exp_datetime = make_aware(
                    datetime.fromtimestamp(exp_timestamp))

                # Create an OutstandingToken entry for the access token
                outstanding_token, created = OutstandingToken.objects.get_or_create(
                    jti=jti,
                    token=access_token,
                    user=request.user,
                    created_at=make_aware(datetime.utcnow()),
                    expires_at=exp_datetime
                )
                # Manually adding the token to Blackist model
                # In this case BlackListed.token is an instance of OutStandingToken
                BlacklistedToken.objects.create(token=outstanding_token)

            response = Response(
                {"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
            response.delete_cookie(ACCESS_TOKEN_COOKIE_KEY)
            response.delete_cookie(REFRESH_TOKEN_COOKIE_KEY)
            return response
        except APIException as e:
            raise e
        except TokenError as e:
            raise TokenBlackListedException()
        except Exception as e:
            print(f"Exception while logging out an user: {type(e).__name__}")
            print(f"Exception error: {e}")
            raise InternalServerErrorException()

# APIView for GoogleLogin setup
# After writing this view Go to GoogleCloud console -> create a project
# then Go to OAuth consent screen and then set the redirect URL as where you want to redirect after successfull login
# Then copy the ClientID and ClientSecret from Google cloud console and then paste it inside the SocialApplications tables inside the DjangoAdmin panel
# Make sure to choose the domains listed below for accepting the request from the API.

# For hitting this API successfully you will have to pass an access_token in the POST body of this API request
# This access_token is obtained from OAuth 2.0 playground: https://developers.google.com/oauthplayground/
# on the input your own scopes type: https://www.googleapis.com/auth/userinfo.email and then click on Authorize API
# Once authorized using your own gmail, Click on Exchange authorization code for tokens button
# You will get an access_token that should be passed in the body of this API
# The response of this API will be the LoginAPI response
class GoogleLoginView(SocialLoginView):
    ''''
    This view is used for logging in via google
    '''
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = config('GOOGLE_REDIRECT_URL')

class HomeAPIView(GenericAPIView):
    '''
    This is an API view that only authenticated users can access
    '''
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({
            "message": _("Welcome to the Home View.")
        })
