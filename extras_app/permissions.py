from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from auth_app.authentication import ServiceAuthentication

class IsSuperAdminOrAdmin(BasePermission):
    """
    Custom permission to allow only super admins (superusers) or admins to access the view.
    """
    message = "You do not have permission. Super admin or admin access is required."

    def has_permission(self, request, view):
        if not (request.user.is_superuser or request.user.is_admin):
            raise PermissionDenied(detail=self.message)
        return True
    

class IsService(BasePermission):
    """
    Custom permission to allow only internal service to access the view.
    """
    message = "You do not have permission."
    
    def has_permission(self, request, view):
        return isinstance(request.internal_service, ServiceAuthentication)
