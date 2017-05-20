#Django HyperText Coffee Pot Protocol Middleware (HTCPCP)

Setup
-----

Install by downloading the source and running:

    python setup.py install

or

    pip install django-cors-middleware

and then add it to your installed apps:

::

    INSTALLED_APPS = (
        ...
        'django-htcpcp',
        ...
    )

You will also need to add a middleware class to listen in on responses:

::

    # Use `MIDDLEWARE_CLASSES` prior to Django 1.10
    MIDDLEWARE = [
        ...
        'django-htcpcp.middleware.HTCPCPMiddleware',
        ...
    ]