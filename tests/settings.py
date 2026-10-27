SECRET_KEY = "htcpcp-tests"
ALLOWED_HOSTS = ["testserver"]
ROOT_URLCONF = "tests.urls"
INSTALLED_APPS = ["djhtcpcp"]
MIDDLEWARE = ["djhtcpcp.middleware.HTCPCPMiddleware"]
USE_TZ = True
