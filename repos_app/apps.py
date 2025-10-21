from django.apps import AppConfig


        
class RepositoryAppConfig(AppConfig):
    name = 'repos_app'

    def ready(self):
        import repos_app.signals