from django.core.management import call_command
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def run_migrations(domain, lock_key):
    """
    Task to run migrations for a specific domain.
    """
    connection.close()  
    cache.set(f"migration_status_{domain}", "running", timeout=60 * 5)  
    try:
        call_command('migrate')  
        cache.set(f"migration_status_{domain}", "completed", timeout=60 * 5)  
        logger.info(f"Migration completed for domain {domain}")
    except:
        pass
    finally:
        cache.delete(lock_key)
