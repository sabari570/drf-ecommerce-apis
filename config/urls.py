"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from allauth.account.views import confirm_email
from dj_rest_auth.views import (
    PasswordResetView, PasswordResetConfirmView, PasswordChangeView)

# For including the API documentation
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# For viewing media files
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('users.urls', namespace='users')),
    path('api/products/', include('products.urls', namespace='products')),
    path('api/cart/', include('cart.urls', namespace='cart')),
    path('api/orders/', include("orders.urls", namespace='orders')),
    path('api/payment/', include('payment.urls', namespace='payment')),

    # This path is added inorder to verify the email address, when a user is registered successfully you get an email with an URL to confirm email
    # on clicking that link you will be redirected to account-confirm-email/ page which hits a GET request
    # on that page on clicking the confirm email button will hit a POST request on this same endpoint thus verifying your email
    # re_path() : This is used for defining URL patterns using regular expressions (regex)
    # Example URLs that satisfies this pattern: /account-confirm-email/NDA:1tdMmL:H_fsasNpvKC3BxMaiAfdldQd4ohSKfkNPKFOhub5tQo/
    re_path(r"^account-confirm-email/(?P<key>[-:\w]+)/$",
            confirm_email, name="account_confirm_email"),

    # This endpoint is for sending a password reset email
    path("api/password/reset/", PasswordResetView.as_view(), name="password reset"),

    # For the password reset email API endpoint to run successfully we will need the password/reset/confirm endpoint to be defined
    # This is the end point which will be sent throught the email and on clicking it you will be able to reset the password
    # you will have 2 additional fields in it uid and token which will be obtained from the URL
    path("api/password/reset/confirm/<str:uidb64>/<str:token>/",
         PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # API endpoint to change the password
    path("api/password/change/", PasswordChangeView.as_view(),
         name="change password"),

    # this is added inorder to avoid the allauth-inactive url issue
    path("", include("allauth.account.urls")),
]

# SCHEMA URLs =>
# This is used to include the API documentation
# Refer documentation: https://drf-spectacular.readthedocs.io/en/latest/readme.html#installation
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# For viewing the media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
