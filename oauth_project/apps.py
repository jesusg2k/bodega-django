from django.apps import AppConfig


class OauthProjectConfig(AppConfig):
    name = 'oauth_project'

    def ready(self):
        import oauth_project.signs

