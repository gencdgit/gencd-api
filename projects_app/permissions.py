from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from auth_app.authentication import JWTOrServiceAuthentication

class IsSuperAdmin(BasePermission):
    """
    Custom permission to allow only super admins (superusers) to access the view.
    """
    message = "You do not have permission. Super admin access is required."

    def has_permission(self, request, view):
        if not request.user.is_superuser:  
            raise PermissionDenied(detail=self.message)
        return True


class IsAdmin(BasePermission):
    """
    Custom permission to allow only admin users to access the view.
    """
    message = "You do not have permission. Admin access is required."

    def has_permission(self, request, view):
        if not request.user.is_admin:  
            raise PermissionDenied(detail=self.message)
        return True


class IsSuperAdminOrAdmin(BasePermission):
    """
    Custom permission to allow only super admins (superusers) or admins to access the view.
    """
    message = "You do not have permission. Super admin or admin access is required."

    def has_permission(self, request, view):
        if not (request.user.is_superuser or request.user.is_admin):
            raise PermissionDenied(detail=self.message)
        return True


class ObjectAccess(IsAuthenticated):
    """
    Custom access to check and allow only users that have access to the object.
    """

    messages = {
        "GET": "You do not have access to view this {object_name}.",
        "PUT": "You do not have access to update this {object_name}.",
        "PATCH": "You do not have access to partially update this {object_name}.",
        "DELETE": "You do not have access to delete this {object_name}.",
        "DEFAULT": "You do not have the required accesss for this action on this {object_name}."
    }

    def get_error_message(self, method, view):
        object_name = getattr(view, "object_name", "object")
        return self.messages.get(method, self.messages["DEFAULT"]).format(object_name=object_name)

    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True

        if request.method == 'GET':
            if obj.accesses.filter(user=request.user).exists():
                return True
            raise PermissionDenied(detail=self.get_error_message('GET', view))

        if request.method in ['PUT', 'PATCH']:
            if obj.accesses.filter(user=request.user, access='admin').exists():
                return True
            raise PermissionDenied(detail=self.get_error_message(request.method, view))

        if request.method == 'DELETE':
            if obj.accesses.filter(user=request.user, access='owner').exists():
                return True
            raise PermissionDenied(detail=self.get_error_message('DELETE', view))

        raise PermissionDenied(detail=self.get_error_message('DEFAULT', view))

class IsService(BasePermission):
    """
    Custom permission to allow only internal service to access the view.
    """
    message = "You do not have permission."
    
    def has_permission(self, request, view):
        if isinstance(request.internal_service, JWTOrServiceAuthentication):
            return True
