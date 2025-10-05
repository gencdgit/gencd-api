import os
from django.contrib.auth.models import BaseUserManager
from django.db import transaction
from helper.validators import valid_email
from helper.exceptions import SmoothException


class UserManager(BaseUserManager):
    """Manager for creating users and superusers with validation and atomic transactions."""
     
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise SmoothException.error(
                detail='The Email field must be set',
                dev_message='Attempted to create a user without providing an email.'
            )

        if not valid_email(email):
            raise SmoothException.error(
                detail='Invalid email address',
                dev_message=f'Provided email "{email}" failed validation.'
            )

        
        # Normalize the email address
        email = self.normalize_email(email)
        
        # Using atomic transactions to ensure all operations succeed or roll back entirely.
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
        return self.create_user(email, password, **extra_fields)        
