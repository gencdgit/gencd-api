import gzip
import uuid
import json
import base64
import logging 
from django.db import models
from auth_app.models import User
from helper.models import UUIDPrimaryKey
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# ANSI color codes
class LogColors:
    OK = "\033[92m"       # Green
    WARNING = "\033[93m"  # Yellow
    ERROR = "\033[91m"    # Red
    RESET = "\033[0m"     # Reset



class CompressedJSONField(models.JSONField):
    SENSITIVE_KEYS = {"password", "secret", "token", "access_token", "api_key", "authorization"}

    def _redact_sensitive(self, data):
        if isinstance(data, dict):
            return {
                key: (self._random_string() if key.lower() in self.SENSITIVE_KEYS else self._redact_sensitive(value))
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._redact_sensitive(item) for item in data]
        return data

    def _random_string(self):
        return "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    def _convert_uuid_to_string(self, value):
        if isinstance(value, dict):
            return {k: self._convert_uuid_to_string(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._convert_uuid_to_string(item) for item in value]
        elif isinstance(value, uuid.UUID):
            return str(value)
        return value

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            redacted = self._redact_sensitive(value)
            redacted = self._convert_uuid_to_string(redacted)
            json_data = json.dumps(redacted).encode('utf-8')
            compressed = gzip.compress(json_data)
            return base64.b64encode(compressed).decode('utf-8')
        except Exception as e:
            raise ValidationError(f"Compression failed: {e}")

    def from_db_value(self, value : str, expression, connection):
        if value is None:
            return value
        try:
            compressed = base64.b64decode(value.encode('utf-8'))
            json_data = gzip.decompress(compressed).decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            raise ValidationError(f"Decompression failed: {e}")

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            return self.from_db_value(value, None, None)
        return value


class Log(UUIDPrimaryKey):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    endpoint = models.CharField(max_length=512)
    http_method = models.CharField(max_length=10)
    request_payload = CompressedJSONField(null=True, blank=True)
    response_payload = CompressedJSONField(null=True, blank=True)
    status_code = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    latency = models.FloatField()
    ip_address = models.GenericIPAddressField()
    headers = CompressedJSONField(null=True, blank=True)
    service = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.user.first_name} - {self.endpoint} - {self.status_code}"


    def log(self):
        if self.status_code >= 500:
            color = LogColors.ERROR
        elif self.status_code >= 400:
            color = LogColors.WARNING
        else:
            color = LogColors.OK

        message = (
            f"[{self.timestamp}] User: {getattr(self.user, 'first_name', 'Anonymous')} | "
            f"IP: {self.ip_address} | Endpoint: {self.endpoint} | "
            f"Method: {self.http_method} | Status: {self.status_code} | "
            f"Latency: {self.latency}s"
        )
        logger.info(color + message + LogColors.RESET)
    
    class Meta:
        ordering = ['-timestamp']
    
    