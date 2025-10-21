from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from auth_app.managers import UserManager
from helper.models import UUIDPrimaryKey, TimeLine, IsActiveModel
from helper.mails import send_new_user_welcome_email, send_password_reset_email
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile


class Role(UUIDPrimaryKey, TimeLine, IsActiveModel):
    """
    Role model for defining user roles.
    Each role contains a list of permission objects (from permissions.json).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    permissions = models.JSONField(default=list, blank=True)
    is_system = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def has_permission(self, slug: str) -> bool:
        """Check if this role contains a permission with given slug."""
        return self.is_super_admin or any(p.get("slug") == slug for p in self.permissions)


class User(AbstractBaseUser, UUIDPrimaryKey, TimeLine, IsActiveModel):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)     
    is_superuser = models.BooleanField(default=False)
    
    email = models.EmailField(
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
                message="Enter a valid email address."
            )
        ]
    )
    profile_picture = models.ImageField(
        upload_to='images/profile_pictures', 
        blank=True, 
        null=True
    )
    
    last_login = models.DateTimeField(null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    objects: UserManager = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email
    
    def send_welcome_email(self):
       return send_new_user_welcome_email(self)
   
    def send_password_reset_email(self, session_token):
       return send_password_reset_email(self, session_token)

    def generate_default_profile_picture(self):
        """ Generate an image with the first letter of the email if no profile picture is set """
        if not self.profile_picture:
            first_letter = self.email[0].upper()
            img_size = (100, 100)  # Image size (adjust as needed)
            background_color = "#a474ff"
            text_color = "white"
            
            # Create image
            img = Image.new("RGB", img_size, background_color)
            draw = ImageDraw.Draw(img)
            
            # Load font (default PIL font if no TTF is found)
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except IOError:
                font = ImageFont.load_default()

            # Get text size and position
            text_size = draw.textbbox((0, 0), first_letter, font=font)
            text_x = (img_size[0] - (text_size[2] - text_size[0])) // 2
            text_y = (img_size[1] - (text_size[3] - text_size[1])) // 2

            # Draw text
            draw.text((text_x, text_y), first_letter, fill=text_color, font=font)

            # Save to a Django-compatible file object
            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)

            # Assign to profile picture field
            file_name = f"images/profile_pictures/{self.email}_default.png"
            self.profile_picture.save(file_name, ContentFile(img_io.read()), save=False)

    def save(self, *args, **kwargs):
        if not self.profile_picture:
            self.generate_default_profile_picture()
        super().save(*args, **kwargs)

