# data_pro/apps.py
from django.apps import AppConfig

class DataProConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_pro'
    label = 'data_pro'

    def ready(self):
        # Import signals only when app is fully loaded
        try:
            import data_pro.signals
        except ImportError:
            pass

