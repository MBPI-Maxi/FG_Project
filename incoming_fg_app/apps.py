from django.apps import AppConfig


class IncomingFgAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incoming_fg_app"

    # def ready(self):
    #     import incoming_fg_app.signals

