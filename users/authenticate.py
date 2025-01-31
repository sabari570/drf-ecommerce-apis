from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken


class CustomJWTCookieAuthentication(JWTCookieAuthentication):
    '''
    This is a custom JWT Cookie authentication class that overrides the authenticate method.
    It extracts the raw_token from the cookie and then validates it by checking it in the BlacklistedTokens model.
    '''

    def authenticate(self, request):
        cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
        header = self.get_header(request)
        if header is None:
            if cookie_name:
                raw_token = request.COOKIES.get(cookie_name)
                # True at your own risk
                if getattr(settings, 'JWT_AUTH_COOKIE_ENFORCE_CSRF_ON_UNAUTHENTICATED', False):
                    self.enforce_csrf(request)
                elif raw_token is not None and getattr(settings, 'JWT_AUTH_COOKIE_USE_CSRF', False):
                    self.enforce_csrf(request)
            else:
                return None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            token = AccessToken(raw_token)

            # Get the JWT ID (jti)
            jti = token['jti']
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise AuthenticationFailed("Token has been Blacklisted")
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            print(f"Exception occured in custom JWT Cookie auth: {str(e)}")
            raise AuthenticationFailed("Invalid or expired token.")
