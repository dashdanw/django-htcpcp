from django.apps import AppConfig


class HTCPCPConfig(AppConfig):
    name = "djhtcpcp"
    verbose_name = "HTCPCP"

    def ready(self):
        from . import checks  # noqa: F401
