import json
from rest_framework.permissions import BasePermission
from auth_app.models import Role
from django.conf import settings
import os

PERMISSIONS_FILE_PATH = settings.BASE_DIR / 'data' / 'permissions.json'

# Load permissions safely
all_permissions_list = []
if os.path.exists(PERMISSIONS_FILE_PATH):
    with open(PERMISSIONS_FILE_PATH, 'r') as f:
        all_permissions_list = json.load(f)
else:
    print(f"⚠️ Warning: Permissions file not found: {PERMISSIONS_FILE_PATH}")


PERMISSIONS_INDEX = {}
for perm in all_permissions_list:
    slug = perm["slug"]
    method = perm["request_method"].upper()
    PERMISSIONS_INDEX.setdefault(slug, {})[method] = perm


class AppPermission(BasePermission):
    """
    Optimized DRF permission class using Role.has_permission.
    Supports 'system.all' as global bypass for all request methods.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        view_permission_slugs = getattr(view, "permission_slugs", [])
        if not view_permission_slugs:
            return True  # no permissions required

        current_method = request.method.upper()
        user_role : Role = getattr(request.user, "role", None)

        if not user_role or not getattr(user_role, "permissions", []):
            return False

        if user_role.is_super_admin:
            return True

        for slug in view_permission_slugs:
            if user_role.has_permission("system.all"):
                return True

            perm_for_method = PERMISSIONS_INDEX.get(slug, {}).get(current_method)

            if perm_for_method and user_role.has_permission(slug):
                return True

        return False
