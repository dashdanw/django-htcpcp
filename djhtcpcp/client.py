"""Django test clients that speak HTCPCP.

>>> client = HTCPCPClient()
>>> client.brew("/coffee/black/", additions=["Cream"]).status_code
202
"""

from django.test import AsyncClient, Client

from .rfc import BREW, COFFEEPOT_MEDIA_TYPE, PROPFIND, START, TEAPOT_MEDIA_TYPE, WHEN


class HTCPCPClientMixin:
    def brew(self, path, command=START, *, tea=False, additions=None, headers=None, **extra):
        headers = dict(headers or {})
        if additions:
            headers["Accept-Additions"] = ", ".join(additions)
        content_type = TEAPOT_MEDIA_TYPE if tea else COFFEEPOT_MEDIA_TYPE
        return self.generic(BREW, path, command, content_type, headers=headers, **extra)

    def when(self, path, **extra):
        return self.generic(WHEN, path, **extra)

    def propfind(self, path, **extra):
        return self.generic(PROPFIND, path, **extra)


class HTCPCPClient(HTCPCPClientMixin, Client):
    pass


class AsyncHTCPCPClient(HTCPCPClientMixin, AsyncClient):
    pass
