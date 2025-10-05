import os
import logging
import requests
from .exceptions import SmoothException

logger = logging.getLogger(__name__)


class InternalRequest:
    """
        Class to handle internal requests to other services.
    """
        
    def __init__(self, service_name, django_rest_framework_request=None):
        if not service_name:
            raise SmoothException.error(
            detail="Service name is required.",
            dev_message="Service name was missing in the request."
        )
        
        self.session = requests.Session()
        self.service_name = service_name
        
        self.internal_secret_key = os.environ.get('INTERNAL_SECRET_KEY')
        if not self.internal_secret_key:
            raise SmoothException.error(
                detail="Internal secret key is missing in settings.",
                dev_message="Ensure that the internal secret key is correctly set in the application settings."
            )
        
        if django_rest_framework_request:
            self.session.headers.update(django_rest_framework_request.headers)
        else:
            self.session.headers.update({"X-Service-Auth": self.internal_secret_key})
    
    def request(self, method: str, endpoint: str, **kwargs):
        """
            Make a request with the specified method while automatically adding the secret key to headers.
        """
        headers = kwargs.pop("headers", {})
        headers.update(self.session.headers)  
        kwargs["headers"] = headers    
            
        url = f"{self.service_name}{endpoint}"
        
        logger.info(f"Making {method} request to {url} with headers: {headers}")
                
        return self.session.request(method, url, **kwargs)
        
    def get(self, endpoint: str, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    @classmethod
    def admin_service(cls, django_rest_framework_request=None):
        """
        Create a CustomRequest instance for the admin service.
        """
        return cls(os.environ.get('ADMIN_BACKEND_DOMAIN'), django_rest_framework_request)

