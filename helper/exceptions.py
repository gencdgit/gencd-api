import traceback
from rest_framework.response import Response


class SmoothException(Exception):
    """Custom exception to handle errors with user and developer messages."""
    
    def __init__(self, detail, dev_message=None, type="error", redirect_url='Not applicable', status_code=400):
        self.detail = detail
        self.dev_message = dev_message or detail  
        self.type = type
        self.redirect_url = redirect_url
        self.status_code = status_code
        self.traceback_info = self._get_traceback_info()
        
        super().__init__(detail)
        
    
    def _get_traceback_info(self):
        """Extracts traceback details including file name, line number, and function name."""
        tb = traceback.extract_stack()[-3]  
        return {
            "file": tb.filename,
            "line": tb.lineno,
            "function": tb.name
        }
    
    def to_dict(self):
        """Returns a dictionary representation of the exception."""
        return {
            "type": self.type,
            "detail": self.detail,
            "dev_message": self.dev_message,
            "redirect_url": self.redirect_url,
            "status_code": self.status_code,
            "traceback_info": self.traceback_info
        }
    
    @classmethod
    def info(cls, detail, dev_message=None, redirect_url='Not applicable'):
        return cls(detail, dev_message, type="info", redirect_url=redirect_url, status_code=400)
    
    @classmethod
    def warning(cls, detail, dev_message=None, redirect_url='Not applicable'):
        return cls(detail, dev_message, type="warning", redirect_url=redirect_url, status_code=400)
    
    @classmethod
    def error(cls, detail, dev_message=None, redirect_url='Not applicable'):
        return cls(detail, dev_message, type="error", redirect_url=redirect_url, status_code=400)
    
    @classmethod
    def critical(cls, detail, dev_message=None, redirect_url='Not applicable'):
        return cls(detail, dev_message, type="critical", redirect_url=redirect_url, status_code=400)



def custom_exception_handler(exc, context):
    """
    Custom exception handler to wrap all errors in a consistent format.
    """
    if isinstance(exc, SmoothException):
        return Response(
            exc.to_dict(),
            status=exc.status_code
        )

    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

        if isinstance(response.data, dict) and not response.data.get('detail'):
            first_error = None
            for field, field_errors in response.data.items():
                if isinstance(field_errors, list) and field_errors:
                    first_error = f"{field}: {field_errors[0]}"
                    break
                elif isinstance(field_errors, str):
                    first_error = f"{field}: {field_errors}"
                    break

            if first_error:
                response.data = {
                    'detail': first_error,
                    'status_code': response.status_code
                }

    return response