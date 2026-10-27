from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

DEFAULT_COFFEE_PATHS = (
    "/coffee/black/",
    "/coffee/espresso/",
)

COFFEE_METHODS = ("BREW", "WHEN")


class HTCPCPMiddleware(MiddlewareMixin):
    """Answer HTCPCP requests (RFC 2324 / RFC 7168).

    * ``BREW`` to a coffee pot starts brewing (202 Accepted).
    * ``WHEN`` to a coffee pot stops the milk (201 Created).
    * ``BREW`` or ``WHEN`` to anything else is a teapot (418 I'm a teapot).

    Coffee pot paths can be overridden with the ``HTCPCP_COFFEE_PATHS`` setting.
    All other requests pass through untouched.
    """

    coffee_methods = COFFEE_METHODS

    @property
    def coffee_list(self):
        return tuple(getattr(settings, "HTCPCP_COFFEE_PATHS", DEFAULT_COFFEE_PATHS))

    def process_request(self, request):
        if request.method not in self.coffee_methods:
            return None

        if request.path not in self.coffee_list:
            return HttpResponse("I'm a teapot.", status=418, content_type="text/plain")

        if request.method == "BREW":
            return HttpResponse("Say WHEN . . . ", status=202, content_type="message/coffeepot")

        return HttpResponse("Mmmmmmm coffee!", status=201, content_type="message/coffeepot")
