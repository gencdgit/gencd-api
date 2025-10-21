from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'repos_app'

    # def ready(self):
    #     import repos_app.signals
        