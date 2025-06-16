# uxo_records/apps.py

from django.apps import AppConfig


class UxoRecordsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uxo_records"

    def ready(self):
        import uxo_records.signals
