from django.apps import AppConfig


class NinjaAPIConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cap.ninja_api"

    def ready(self):
        # Import signals to ensure they are registered
        pass
