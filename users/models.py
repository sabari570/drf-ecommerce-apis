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
from django_countries.fields import CountryField

# This is used for django signals
from django.dispatch import receiver
# This is the type of Signal we need
from django.db.models.signals import post_save

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
    is_active = models.BooleanField(_("active status"), default=True, help_text=(
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

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between
        '''
        if self.firstname and self.lastname:
            return f"{self.firstname} {self.lastname}".strip()
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


# Model that contains fields regarding the user's profile
class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name='profile', on_delete=models.CASCADE)
    # Here, the upload_to='avatar' part means that uploaded avatar images will be stored in a
    # folder named avatar within the media directory (the default directory for media files in Django)
    avatar = models.ImageField(upload_to='avatar', blank=True)
    bio = models.CharField(max_length=200, blank=True)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        # when fetched the profile details are oredered in descending order
        ordering = ("-created_at",)

    def __str__(self):
        return self.user.get_full_name()


# Model the notes the address of the user for shipping purpose
class Address(models.Model):
    # Address options
    BILLING = "B"
    SHIPPING = "S"

    ADDRESS_CHOICES = ((BILLING, _("billing")), (SHIPPING, _("shipping")))

    # To identify this address belongs to which user
    # One user can have muliple addresses
    user = models.ForeignKey(
        CustomUser, related_name='addresses', on_delete=models.CASCADE)
    # For the 'address_type' field Django handles this in the Following way:
    # ADDRESS_CHOICES:->
    #   * Django stores the first value in the database.
    #   * The second value is only for display in forms or Django admin.
    #   * While sending API request we should send it as 'B' or 'S'
    #   * If you try sending "billing" or "shipping", Django will raise a ValidationError because it expects "B" or "S".
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    country = CountryField()
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.user.get_full_name()


# ********************** THIS SECTION CONTAINS THE SIGNALS CODE **********************
# Here is where we write django signals needed when models are created
# Now i need to create a Profile object, after a user gets saved to the DB
# This means it is a post_save signal and the sender is User

# Explanation:
#   what is happening is when the User model is saved, a signal is fired called create_profile which creates a Profile instance with a foreign key pointing to the instance of the user. The other method save_profile just saves the instance.

#   Now let’s understand the arguments

#   receiver – The function who receives the signal and does something.
#   sender – Sends the signal
#   created (only availabel in post_save) — Checks whether the model is created or not (boolean val1ue returns true if User is created successfully)
#   instance — created model instance
#   **kwargs –wildcard keyword arguments
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # This connects the User with the Profile model
    instance.profile.save()

# Signal to create a cart when a user is created


@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        # This is imported in here inorder to avoid circular imports
        from cart.models import Cart
        Cart.objects.create(user=instance)
