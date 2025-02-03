from rest_framework.permissions import BasePermission


class IsUserProfileOwner(BasePermission):
    '''
    Checks if the authenticated user is the owner of the profile
    '''

    def has_object_permission(self, request, view, obj):
        # the obj we get in here is the obj returned by get_object() from the Profile APIView
        # so here the obj is a Profile instance
        return obj.user == request.user or request.user.is_staff


class IsUserAddressOwner(BasePermission):
    '''
    Checks if the authenticated user is the owner of the address
    '''
    # This says whether the user has permission to access this APIView
    # this can also be provided inside the permission_classes list as [permissions.isAuthenticated]
    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
