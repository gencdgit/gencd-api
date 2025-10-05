from django.conf import settings
from helper.exceptions import SmoothException
import ipaddress

class InternalAPIMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.internal_secret_key = getattr(settings, "INTERNAL_SECRET_KEY_KEY", None)
        self.allowed_hosts = {"user-service", "chat-service", "gateway-service"}  
        self.internal_network = ipaddress.ip_network("172.16.0.0/12", strict=False)

    def __call__(self, request):
        INTERNAL_API_PREFIX = "/api/internal"

        if request.path.startswith(INTERNAL_API_PREFIX):
            # Check Auth Header
            auth_header = request.headers.get("X-Service-Auth")
            if auth_header != self.internal_secret_key:
                raise SmoothException.error(
                    detail="Invalid service authentication token.",
                    dev_message="Unauthorized service attempted to access internal API.",
                    status_code=401
                )

            # Check Internal IP
            client_ip = request.META.get("REMOTE_ADDR", "")
            try:
                ip_addr = ipaddress.ip_address(client_ip)
                if ip_addr not in self.internal_network:
                    raise SmoothException.error(
                        detail="Forbidden: Invalid Internal IP",
                        dev_message=f"Request from unauthorized IP: {client_ip}",
                        status_code=403
                    )
            except ValueError:
                raise SmoothException.error(
                    detail="Invalid IP Address",
                    dev_message=f"Received malformed IP address: {client_ip}",
                    status_code=400
                )

            # Check Hostname
            request_host = request.get_host().split(":")[0]
            if request_host not in self.allowed_hosts:
                raise SmoothException.error(
                    detail="Forbidden: Invalid Hostname",
                    dev_message=f"Request from unauthorized hostname: {request_host}",
                    status_code=403
                )

        return self.get_response(request)
