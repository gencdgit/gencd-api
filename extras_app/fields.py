import json
import gzip
import base64
import random
import string
from django.db import models
from helper.classes import EncryptionHelper
from django.core.exceptions import ValidationError


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.encryption_helper = EncryptionHelper()
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Prepare value for database storage by encrypting it."""
        if value is None:
            return value
        return self.encryption_helper.encrypt(value)

    def from_db_value(self, value, expression, connection):
        """Decrypt value when fetching from the database."""
        if value is None:
            return value
        try:
            return self.encryption_helper.decrypt(value)
        except Exception:
            raise ValidationError("Decryption failed.")

class EncryptedJSONField(models.JSONField):
    def __init__(self, *args, **kwargs):
        self.encryption_helper = EncryptionHelper()
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None:
            return value
        json_data = json.dumps(value)  
        return self.encryption_helper.encrypt(json_data)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            json_data = self.encryption_helper.decrypt(value)
            return json.loads(json_data)  
        except Exception:
            raise ValidationError("Decryption failed.")


class CompressedJSONField(models.TextField):
    # Define keys to redact
    SENSITIVE_KEYS = {"password", "secret", "token", "access_token", "api_key"}

    def _redact_sensitive(self, data):
        """Redact sensitive keys in a nested dictionary."""
        if isinstance(data, dict):
            return {
                key: (self._random_string(8) if key.lower() in self.SENSITIVE_KEYS else self._redact_sensitive(value))
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._redact_sensitive(item) for item in data]
        return data

    def _random_string(self, length=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            # Redact sensitive fields before storing
            redacted = self._redact_sensitive(value)
            json_data = json.dumps(redacted).encode('utf-8')
            compressed = gzip.compress(json_data)
            return base64.b64encode(compressed).decode('utf-8')
        except Exception as e:
            raise ValidationError(f"Compression failed: {e}")

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            compressed = base64.b64decode(value.encode('utf-8'))
            json_data = gzip.decompress(compressed).decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            raise ValidationError(f"Decompression failed: {e}")

    def to_python(self, value):
        if isinstance(value, dict) or value is None:
            return value
        return self.from_db_value(value, None, None)
