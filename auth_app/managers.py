import os
from django.contrib.auth.models import BaseUserManager
from django.db import transaction
from helper.validators import valid_email
from helper.exceptions import SmoothException

class UserManager(BaseUserManager):
    """Manager for creating users and superusers with validation and atomic transactions."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise SmoothException.error(detail='Email must be set')
        if not valid_email(email):
            raise SmoothException.error(detail='Invalid email address')

        email = self.normalize_email(email)
        with transaction.atomic():
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
        return user

    def create_adminuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)

    def create_special_adminuser(self, **extra_fields):
        extra_fields.setdefault('email', os.environ.get('SPECIAL_ADMIN_EMAIL', None))
        extra_fields.setdefault('password', os.environ.get('SPECIAL_ADMIN_PASSWORD', None))
        return self.create_user(**extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role_id', 1)  
        return self.create_user(email, password, **extra_fields)

