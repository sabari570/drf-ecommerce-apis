from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model, authenticate
from .models import PhoneNumber
from .exceptions import (AccountNotRegisteredException,
                         InvalidCredentialExceptions, AccountDisabledException)
from django.conf import settings

User = get_user_model()


# Here we are creating the serializer for UserRegistration
# This UserRegistrationSerializer inherits the RegisterSerializer inorder to perform the authentication
# Here since we have the RegistrationSerializer we dont have to explicitly mention the User class because
# the RegitrationSerialzier has an adapter that takes the user class and saves it
class UserRegistrationSerializer(RegisterSerializer):
    '''
    Serializer for registring new users using email or phone number
    '''
    username = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(required=False)
    phone_number = PhoneNumberField(
        required=False,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=PhoneNumber.objects.all(),
                message=_("A user is already registered with this phone number")
            )
        ]
    )

    def validate(self, validated_data):
        email = validated_data.get("email")
        phone_number = validated_data.get("phone_number")

        if not (email or phone_number):
            raise serializers.ValidationError(
                _("Enter an email or phone number."))

        if validated_data["password1"] != validated_data["password2"]:
            raise serializers.ValidationError(_("Passwords do not match"))

        return validated_data

    def create_phone(self, user, validated_data):
        phone_number = validated_data.get("phone_number")
        if phone_number:
            # this creates a new PhoneNumber record with the user and phonenumber data
            PhoneNumber.objects.create(user=user, phone_number=phone_number)
            user.phone.save()   # this connects the user with the phone number instance

    # This custom signup function is automatically called when the user is registered by the serializer
    # After the user is saved to the DB, the phone number is created and then added to the DB linking the user and PhoneNumber instance
    def custom_signup(self, request, user):
        self.create_phone(user=user, validated_data=self.validated_data)


# Creating a PhoneNumber serializer
class PhoneNumberSerializer(serializers.ModelSerializer):
    '''
    Serialzier class to serialize phone number
    '''
    phone_number = PhoneNumberField()

    class Meta:
        model = PhoneNumber
        # The fields attribute inside the Meta class specifies which fields of the model should
        # be included in the serialized data when you're working with Django REST framework serializers.
        # If you want all fields: You can use fields = '__all__'
        # If you want specific fields: You can list them out like this: fields = ('phone_number', 'is_verified', 'created_at')
        # Excluding fields: If you want to exclude some fields, you can use exclude: exclude = ('created_at',)
        fields = ("phone_number",)

    # In Django REST framework, the standard way to validate a specific field within a ModelSerializer is by defining a validate_<field_name> method.
    def validate_phone_number(self, value):
        try:
            queryset = User.objects.get(phone__phone_number=value)
            if queryset.phone.is_verified == True:
                err_message = _("Phone number is already verified")
                raise serializers.ValidationError(err_message)
        except User.DoesNotExist:
            raise AccountNotRegisteredException()
        return value


# This is the UserLoginSerializer
class UserLoginSerializer(LoginSerializer):
    '''
    Serializer which is used to serialize users logging in via email or phone and password
    '''
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    password = serializers.CharField(required=True, write_only=True, style={
                                     'input-type': 'password'})

    # This is the format of how the custom authenticate function inside the EmailAuthBackend and PhoneAuthBackend should be called
    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    # The _ in the begining indicates that this is a private function
    # This function actually authenticates the user based on email or phone_number and password
    # and then returns the user instance from the DB
    def _validate_phone_email(self, email, phone_number, password):
        user = None
        if email and password:
            user = self.authenticate(username=email, password=password)
        elif phone_number and password:
            user = self.authenticate(username=str(
                phone_number), password=password)
        else:
            raise serializers.ValidationError(
                _("Enter a phone number or email and password."))
        return user

    # This function is used to validate the data obtained from the serializer
    def validate(self, validated_data):
        email = validated_data.get("email")
        phone_number = validated_data.get("phone_number")
        password = validated_data.get("password")
        user = self._validate_phone_email(
            email=email, phone_number=phone_number, password=password)

        # If the user credentials are incorrect then
        if not user:
            raise InvalidCredentialExceptions()

        # If the user is disabled by setting the is_active to false
        if not user.is_active:
            raise AccountDisabledException()

        # return the user only if the user email address registered is verified
        # verification is done by sending a confirmation mail
        if email:
            # In Django's ORM, the _set suffix is automatically created for reverse relations when using a
            # ForeignKey or OneToManyField. It allows you to access related objects from the other side of the relationship.
            # the _set can be removed if we use the related_name parameter while creating the EmailAddress model
            # since the EmailAddress is automatically created by the allauth package it doesnt have the related_name field and \
            # thats why inorder to access the user related email addresses we need the _set
            # User and EmailAddress model has a one-to-many relationship
            email_address = user.emailaddress_set.filter(
                email=user.email, verified=True).exists()
            if not email_address:
                raise serializers.ValidationError(_("E-mail is not verified"))
        else:
            # Here we dont filter them because User and PhoneNumber has a one-to-one relationship so we
            # can access the phone number of a user directly
            if not user.phone.is_verified:
                raise serializers.ValidationError(
                    _("Phone number is not verified"))

        validated_data["user"] = user
        return validated_data


class PhoneNumberVerificationSerializer(serializers.Serializer):
    '''
    Serializer used to verify the phone number with the OTP generated for it
    '''
    phone_number = PhoneNumberField(required=True)
    otp = serializers.CharField(
        required=True, max_length=settings.TOKEN_LENGTH)

    def validate_phone_number(self, value):
        user = User.objects.filter(phone__phone_number=value).exists()
        if not user:
            raise AccountNotRegisteredException()
        return value

    def validate(self, validated_data):
        phone_number = validated_data.get("phone_number")
        otp = validated_data.get("otp")
        phoneNumber_instance = PhoneNumber.objects.get(
            phone_number=phone_number)
        phoneNumber_instance.check_verification(security_code=otp)
        return validated_data
