# taller_core/gestion/apps.py

from django.apps import AppConfig


class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'
    verbose_name = 'Gestión de Taller'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        try:
            import gestion.signals
            print("✓ Signals importados correctamente")
        except ImportError as e:
            print(f"⚠️ Error al importar signals: {e}")
