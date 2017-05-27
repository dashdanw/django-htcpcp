Django HyperText Coffee Pot Protocol Middleware (HTCPCP)
-----
Implemented HTCPCP as per RFC 2324.

https://www.ietf.org/rfc/rfc2324.txt

Setup
-----

Install by downloading the source and running:

    python setup.py install

or

    pip install django-htcpcp

and then add it to your installed apps:

    INSTALLED_APPS = (
        ...
        'djhtcpcp',
        ...
    )

You will also need to add a middleware class to listen in on responses:

Django 1.10+

    MIDDLEWARE = [
        ...
        'djhtcpcp.middleware.HTCPCPMiddleware',
        ...
    ]

Django 1.8-1.10:

    MIDDLEWARE_CLASSES = [
        ...
        'djhtcpcp.middleware.HTCPCPMiddleware',
        ...
    ]