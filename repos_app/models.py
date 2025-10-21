from django.db import models
from django.utils.timezone import now, timedelta
from django.core.validators import RegexValidator
from helper.models import UUIDPrimaryKey, TimeLine
from helper.mails import send_invitation_email
from projects_app.models import Project
    
       
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

class Repository(UUIDPrimaryKey,TimeLine):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=255)
    repo_url = models.URLField(max_length=500)
    branch = models.CharField(max_length=100, default='main')
    is_private = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    last_doc_generated_at = models.DateTimeField(blank=True, null=True)
    ssh_key_path = models.CharField(max_length=255, default='keys/public_key.pem')


    class Meta:
        unique_together = ('project', 'repo_url', 'branch')

    def __str__(self):
        return f"{self.project.name} - {self.name}"