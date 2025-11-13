
from django.apps import AppConfig
class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import gestion.signals  # Esto activa los signals


