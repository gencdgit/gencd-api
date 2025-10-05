import os
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.functional import LazyObject
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import helper


class LazyUserModel(LazyObject):
    def _setup(self):
        self._wrapped = get_user_model()

User = LazyUserModel()

class JWTSessionAuthentication(BaseAuthentication):
    """
    Custom authentication class that uses a JWT token from the 'Authorization' header
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            raise AuthenticationFailed('Authorization header is required for authentication.')

        try:
            token = auth_header.split()[1]
        except IndexError:
            raise AuthenticationFailed('Invalid token header. No token provided.')

        try:
            decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            session_key = decoded_payload.get('session_key')
            if not session_key:
                raise AuthenticationFailed('Invalid token payload.')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        session_data = helper.utils.retrieve_session(session_key)
        if not session_data:
            raise AuthenticationFailed('Invalid session.')

        user_id = session_data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        
        if not user.is_active:
            raise AuthenticationFailed('User is inactive.')
        
        request.decoded_payload = decoded_payload
        return (user, decoded_payload)

    def authenticate_header(self, request):
        """
        Return a string to be used in the 'WWW-Authenticate' header.
        This is used when the authentication fails.
        """
        return 'Bearer'

class ServiceAuthentication(BaseAuthentication):
    """
    Custom authentication class to validate requests from internal services
    (e.g., admin service) using a shared token.
    """
    
    def authenticate(self, request):
        service_token = request.headers.get('X-Service-Auth')
        internal_secret_key = os.environ.get('INTERNAL_SECRET_KEY')
        if not service_token:
            raise AuthenticationFailed('Missing service authentication token.')
        if service_token != internal_secret_key:
            raise AuthenticationFailed('Invalid service authentication token.')
        request.internal_service = self
        return (None, None)

class JWTOrServiceAuthentication(BaseAuthentication):
    """
    Custom authentication class that first checks for X-Service-Auth.
    If not present, it falls back to JWT token authentication.
    """

    def authenticate(self, request):
        # 1. Check for Service Authentication
        service_token = request.headers.get('X-Service-Auth')
        internal_secret_key = os.environ.get('INTERNAL_SECRET_KEY')

        if service_token:
            if service_token == internal_secret_key:
                request.internal_service = JWTOrServiceAuthentication
                return (None, None)  # Service is authenticated, no user needed
            else:
                raise AuthenticationFailed('Invalid service authentication token.')

        # 2. Check for JWT Token Authentication
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token = auth_header.split()[1]
        except IndexError:
            raise AuthenticationFailed('Invalid token header. No token provided.')

        try:
            decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            session_key = decoded_payload.get('session_key')
            if not session_key:
                raise AuthenticationFailed('Invalid token payload.')
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        session_data = helper.utils.retrieve_session(session_key)
        if not session_data:
            raise AuthenticationFailed('Invalid session.')

        user_id = session_data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
        
        if not user.is_active:
            raise AuthenticationFailed('User is inactive.')
        
        request.decoded_payload = decoded_payload
        return (user, decoded_payload)

    def authenticate_header(self, request):
        return 'Bearer'

    """
    Custom authentication class to validate requests from internal services 
    (e.g., admin service) using a shared token.
    """

    def authenticate(self, request):
        service_token = request.headers.get('X-Service-Auth')
        INTERNAL_SECRET_KEY = os.environ.get('INTERNAL_SECRET_KEY')
        
        if not service_token:
            raise AuthenticationFailed('Missing service authentication token.')

        if service_token != INTERNAL_SECRET_KEY:
            raise AuthenticationFailed('Invalid service authentication token.')

        request.internal_service = self
        return (None, None)