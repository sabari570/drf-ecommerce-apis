from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from .serializers import (UserRegistrationSerializer, PhoneNumberSerializer,
                          UserLoginSerializer, PhoneNumberVerificationSerializer)
from .utils import send_or_resend_sms
from rest_framework.exceptions import APIException
from .exceptions import InternalServerErrorException
# this is for including transactions in our API while interacting with DB
from django.db import transaction

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
