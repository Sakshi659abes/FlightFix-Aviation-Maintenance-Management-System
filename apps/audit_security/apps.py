from django.apps import AppConfig

class AuditSecurityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit_security'
    verbose_name = 'Security, Audit Trail & System Roles'
