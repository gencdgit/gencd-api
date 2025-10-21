from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects_app'

    # def ready(self):
    #     import projects_app.signals
        