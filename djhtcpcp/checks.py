from django.core.checks import Error, register
from django.core.exceptions import ImproperlyConfigured

from .pots import get_pots


@register()
def check_pots(app_configs, **kwargs):
    try:
        get_pots()
    except ImproperlyConfigured as exc:
        return [Error(str(exc), hint="See the django-htcpcp README.", id="djhtcpcp.E001")]
    return []
