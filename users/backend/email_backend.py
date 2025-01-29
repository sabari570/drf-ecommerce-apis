from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

# This EmailAuthBackend is created inorder to customize the login of the app so that we can login using email and password
class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        Overrides the default authenticate method that usually allows user to login using username and password.
        To allowing users to login using their email id and password.
        '''
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        '''
        Overrides the get_user method to allow users to log in using their email address.
        '''
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
