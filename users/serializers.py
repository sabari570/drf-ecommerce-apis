from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dj_rest_auth.registration.serializers import RegisterSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model
from .models import PhoneNumber
from .exceptions import (AccountNotRegisteredException)

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
    email = serializers.EmailField(required=True)
    phone_number = PhoneNumberField(
        required=True,
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
