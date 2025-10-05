from django.db import models

    
class UserPermissionsManager(models.Manager):
    """Manager for handling user permissions-related operations."""
                
    def create_for_superuser(self, user):
        """
        Creates a new UserPermissions instance for the given user with superuser permissions.
        """

        obj = self.create(user=user)
        obj.grant_admin_permissions()
        return obj
        
    def create_for_admin(self, user):
        """
        Creates a new UserPermissions instance for the given user with admin permissions.
        """
        
        obj = self.create(user=user)
        obj.grant_admin_permissions()
        return obj