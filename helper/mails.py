from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import threading


class EmailThread(threading.Thread):
    def __init__(self, subject, receiver_email, template_name, context):
        self.subject = subject
        self.receiver_email = receiver_email
        self.template_name = template_name
        self.context = context
        super().__init__()

    def run(self):
        html_content = render_to_string(self.template_name, self.context)
        email = EmailMessage(
            subject=self.subject,
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[self.receiver_email],
        )
        email.content_subtype = "html"  
        email.send()


def send_email(subject: str, receiver_email: str, template_name: str, context: dict):
    EmailThread(subject, receiver_email, template_name, context).start()


def send_new_user_welcome_email(user):
    subject = "Welcome to Gene"
    receiver_email = user.email
    template_name = "email/welcome_user.html"
    context = {
        "user_name": user.full_name,
        "user_email": user.email,
    }
    send_email(subject, receiver_email, template_name, context)

def send_invitation_email(invitation):
    subject = "Invitation to join GenCD"
    receiver_email = invitation.to_email
    template_name = "email/invitation_org.html"
    access_url = invitation.access_url
    if access_url.endswith("/"):
        access_url = access_url[:-1]
    join_url = access_url + settings.FRONTEND_LOGIN_PATH + "?invitation_id=" + str(invitation.id)

    context = {
        "invitation_email": invitation.to_email,
        "join_url": join_url,
    }
    send_email(subject, receiver_email, template_name, context)
    
def send_password_reset_email(user, session_token):
    subject = "Password Reset"
    receiver_email = user.email
    full_name = user.full_name
    template_name = "email/password_reset.html"
    access_url = settings.FRONTEND_DOMAIN
    if access_url.endswith("/"):
        access_url = access_url[:-1]
        
    reset_url = access_url + "/reset-password?session_token=" + str(session_token)
    context = {
        "reset_url": reset_url,
        "full_name" : full_name
    }
    send_email(subject, receiver_email, template_name, context)