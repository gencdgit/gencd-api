import os
import json
import time
import logging
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework.response import Response
from django.db import DatabaseError
from django.utils.deprecation import MiddlewareMixin
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS
from django.http import JsonResponse
from django.core.cache import cache
from psycopg2 import ProgrammingError as PsycopgProgrammingError, OperationalError as PsycopgOperationalError, DatabaseError as PsycopgDatabaseError
from psycopg2.errors import UndefinedTable, UndefinedColumn, DuplicateColumn
from django.db.utils import ProgrammingError, OperationalError, DatabaseError
from django.core.exceptions import FieldError
from config.thread_pool import executor
from extras_app import models
from extras_app.tasks import run_migrations

logger = logging.getLogger(__name__)


class LoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.service = os.environ.get('SERVICE', 'Unknown')

    def __call__(self, request: HttpRequest):
        start_time = time.time()

        # Store request body
        request_body = self._get_request_payload(request)

        response : Response = self.get_response(request)
        if request.path.startswith('/api/user/logs'):
            return response
        
        if response.status_code in (301, 302):
            return response
        
        duration = round(time.time() - start_time, 4)

        try:
            user = getattr(request, 'user', None)
            if isinstance(user, models.User):
                user = user
            if isinstance(user, AnonymousUser):
                user = None

            log = models.Log.objects.create(
                user_id=str(user.id) if user else None,
                endpoint=request.path,
                http_method=request.method,
                request_payload=request_body,
                response_payload=self._get_response_payload(response),
                status_code=response.status_code,
                latency=duration,
                ip_address=self._get_client_ip(request),
                headers=dict(request.headers),
                service = self.service
            )
            log.log()  
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to log request: {str(e)}")

        return response

    def _get_request_payload(self, request : HttpRequest):
        try:
            if request.content_type == 'application/json':
                return json.loads(request.body.decode('utf-8'))
            if request.POST:
                return dict(request.POST)
        except Exception:
            pass
        return {}

    def _get_response_payload(self, response : Response):
        try:
            if hasattr(response, 'data'):
                return response.data  # DRF Response
            if hasattr(response, 'content'):
                return self._get_exception_details(response.content)
        except Exception:
            pass
        return {}

    def _get_client_ip(self, request : HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    
    def _get_exception_details(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract error title
        error_title = soup.find("h1").get_text(strip=True)

        # Extract exception value
        exception_value = soup.find("pre", class_="exception_value").get_text(strip=True)

        # Extract rows from the table
        meta_table = soup.find("table", class_="meta")
        rows = meta_table.find_all("tr")

        # Helper to get table data
        data = {}
        for row in rows:
            key = row.find("th").get_text(strip=True).rstrip(":")
            value = row.find("td").get_text(strip=True)
            data[key] = value

        # Parse exception location
        location_text = data.get("Exception Location")
        if location_text:
            parts = location_text.split(",")
            file_path = parts[0].strip()
            line_info = parts[1].strip() if len(parts) > 1 else ""
            line_number = int(line_info.replace("line", "").replace("in post", "").strip()) if "line" in line_info else None
        else:
            file_path = line_number = None

        return {
            "error_title": error_title,
            "exception_type": data.get("Exception Type"),
            "exception_value": exception_value,
            "request_method": data.get("Request Method"),
            "request_url": data.get("Request URL"),
            "django_version": data.get("Django Version"),
            "python_version": data.get("Python Version"),
            "exception_location": {
                "file": file_path,
                "line": line_number,
                "function": "post"
            },

            "raised_during": data.get("Raised during"),
            "timestamp": data.get("Server time")
        }


class AutoDBMigrationManageMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        """Initialize the middleware with the get_response function."""
        self.get_response = get_response


    def apply_migrations(self, domain):
        """Applies migrations using a cache-based lock to prevent race conditions."""
        lock_key = f"migration_lock:{domain}"

        if cache.add(lock_key, "locked", timeout=300):  
            cache.set(f"migration_status_{domain}", "running", timeout=300)

            def _run():
                try:
                    logger.info(f"🔨 Starting migration for domain: {domain}...")
                    run_migrations(domain, lock_key)
                except Exception as e:
                    logger.error(f"❌ Error applying migration for domain {domain}: {str(e)}")

            executor.submit(_run)
        else:
            logger.info(f"⏳ Migration lock already held for domain: {domain}")
            
    
    def is_migrations_available(self):
        connection = connections[DEFAULT_DB_ALIAS]
        executor : MigrationExecutor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)
        pending = [
            {"app": mig[0].app_label, "name": mig[0].name}
            for mig in plan
        ]
        return bool(pending)


    def process_exception(self, request, exception):
        domain = request.headers.get("X-Frontend-Domain")
                
        if isinstance(exception, (
            ProgrammingError,
            OperationalError,
            DatabaseError,
            FieldError,

            ## psycopg errors
            PsycopgProgrammingError,
            PsycopgOperationalError,
            PsycopgDatabaseError,                
            UndefinedTable,
            UndefinedColumn, 
            DuplicateColumn
        )):
            logger.warning(f"⚠️ Migration-related error occurred for domain: {domain}.")
            if self.is_migrations_available():
                self.apply_migrations(domain)
                return JsonResponse({"detail": "DB Migrations are applying. Please try again later."}, status=503)
        
        return None

    def __call__(self, request):
        """Middleware entry point: checks for migration errors, applies migrations if needed."""
        domain = request.headers.get("X-Frontend-Domain")
        

        if not domain:
            logger.warning("❗ Missing 'X-Frontend-Domain' header in request.")
            return JsonResponse({"detail": "Missing domain header."}, status=400)

        migration_status = cache.get(f"migration_status_{domain}")

        if migration_status == "running":
            logger.info(f"⏳ DB Migrations for domain {domain} are currently running.")
            return JsonResponse({
                "detail": "DB Migrations are still running. Please try again later."
            }, status=503)

        return self.get_response(request)