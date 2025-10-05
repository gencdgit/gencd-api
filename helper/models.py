import uuid
from django.db import models

class IsActiveModel(models.Model):
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        

class UUIDPrimaryKey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class TimeLine(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)                   

    class Meta:
        abstract = True
        
        
class Permissions():
    gpt_suite = models.BooleanField(default=False)
    agentic_ai = models.BooleanField(default=False)
    vista_ai = models.BooleanField(default=False)
    orchestration = models.BooleanField(default=False)
    custom_ai_and_ml = models.BooleanField(default=False)
    omnl_channel = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
