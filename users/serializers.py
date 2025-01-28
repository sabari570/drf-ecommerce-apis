from rest_framework import serializers
from rest_framework import validators
from dj_rest_auth.registration.serializers import RegisterSerializer


# Here we are creating the serializer for UserRegistration
# This UserRegistrationSerializer inherits the RegisterSerializer inorder to perform the authentication
class UserRegistrationSerializer(RegisterSerializer):
    '''
    Serializer for registring new users using email or phone number
    '''
    username = serializers.CharField(max_length=30, required=True)
    email = serializers.EmailField(required=True)
