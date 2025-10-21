from django.db import models
from django.utils.timezone import now, timedelta
from django.core.validators import RegexValidator
from helper.models import UUIDPrimaryKey, TimeLine, IsActiveModel
from helper.mails import send_invitation_email
from django.conf import settings
    
       
class Invitation(UUIDPrimaryKey, TimeLine):
    from_email = models.EmailField(
        null=True,
        validators=[
            RegexValidator(
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                message="Enter a valid email address."
            )
        ]
    )
    to_email = models.EmailField(
        
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                message="Enter a valid email address."
            )
        ]
    )
    
    token = models.TextField(unique=True)
    access_url = models.URLField(null=False, blank=False)
    is_accepted = models.BooleanField(default=False)
    
    @property    
    def is_expired(self):
        return self.is_accepted or self.created_at < now() - timedelta(days=1)        
    
    def send_invitation_email(self):
        return send_invitation_email(self)
    

    def __str__(self):
        return f"To - {self.email}"


## Project Model

class Project(UUIDPrimaryKey,TimeLine ):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    repository_count = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.name


