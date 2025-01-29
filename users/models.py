from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth import get_user_model
# For adding a phone_number field to the model
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings    # For getting the settings configuratiom
# inorder to get a random string for OTP
from django.utils.crypto import get_random_string
import datetime  # For converting the time from settings inorder to check the token time limit
# inroder to save the timestamp for security code sent
from django.utils import timezone
# when verification code is not verified
from rest_framework.exceptions import NotAcceptable

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        if not username:
            raise ValueError("Users must have an username")
        email = self.normalize_email(email=email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=30, unique=True)
    firstname = models.CharField(_("first name"), max_length=30, blank=True)
    lastname = models.CharField(_("last name"), max_length=30, blank=True)
    is_staff = models.BooleanField(_("staff status"), default=False, help_text=(
        "Designates whether the user can log into this admin site."))
    is_active = models.BooleanField(_("active status"), default=False, help_text=(
        "Designates whether the user should be treated as active. ""Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("date joined"), default=now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username


# Accessing the User model we created
User = get_user_model()

# Creating a PhoneNumber model


class PhoneNumber(models.Model):
    # hen you set related_name='phone' in the PhoneNumber model, it creates a virtual field
    # named phone inside the User model, allowing you to access the related PhoneNumber instance directly from a User instance.
    user = models.OneToOneField(
        User, related_name='phone', on_delete=models.CASCADE)
    phone_number = PhoneNumberField(unique=True)
    security_code = models.CharField(max_length=120)
    is_verified = models.BooleanField(default=False)
    sent = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # This means when we fetch the data we order them in descending order of created_at -> '-created_at'
        ordering = ("-created_at",)

    # This means when you try to print an instance of PhoneNumber, it will return self.phone_number.as_e164.
    def __str__(self):
        # E.164 is an international standard format for phone numbers, defined by the International Telecommunication Union (ITU).
        # Eg: original-> +1 415-123-4567:: output-> +14151234567 (with e164 format)
        # Eg: original-> +1 415-123-4567:: output-> (415) 123-4567 (withour e164 format)
        return self.phone_number.as_e164

    def generate_security_code(self):
        '''
        Returns a unique 'security_code' for given 'TOKEN_LENGTH' in the settings.
        Default token length = 6
        '''
        # First way of extracting the data from settings
        token_length = getattr(settings, "TOKEN_LENGTH", 6)
        return get_random_string(token_length, allowed_chars="0123456789")

    def is_security_code_expired(self):
        # Second way of extracting the data from settings
        expiration_date = self.sent + \
            datetime.timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        return expiration_date <= timezone.now()

    def send_confirmation(self):
        self.security_code = self.generate_security_code()
        print(
            f"The generated Security code: {self.security_code} to phone number: {self.phone_number}")
        self.sent = timezone.now()
        self.save()
        return self.security_code

    def check_verification(self, security_code):
        if (not self.is_security_code_expired() and
           security_code == self.security_code and
           self.is_verified == False    # if not verified before
            ):
            self.is_verified = True
            self.save()
        else:
            raise NotAcceptable(
                _("Your security code is wrong, expired or this phone is verified before"))
        return self.is_verified
