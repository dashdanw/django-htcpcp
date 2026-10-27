# django-htcpcp

[![PyPI](https://img.shields.io/pypi/v/django-htcpcp.svg)](https://pypi.org/project/django-htcpcp/)
[![CI](https://github.com/dashdanw/django-htcpcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dashdanw/django-htcpcp/actions/workflows/ci.yml)

Django middleware implementing the HyperText Coffee Pot Control Protocol
(HTCPCP), as specified in [RFC 2324](https://www.rfc-editor.org/rfc/rfc2324)
and extended by [RFC 7168](https://www.rfc-editor.org/rfc/rfc7168).

| Request                     | Response                    |
| --------------------------- | --------------------------- |
| `BREW` to a coffee pot      | `202 Accepted` — "Say WHEN" |
| `WHEN` to a coffee pot      | `201 Created` — coffee!     |
| `BREW`/`WHEN` anywhere else | `418 I'm a teapot`          |
| Anything else               | Passed through untouched    |

## Requirements

- Python 3.10+
- Django 4.2+

## Installation

```bash
pip install django-htcpcp
```

Add the middleware to your settings:

```python
MIDDLEWARE = [
    # ...
    "djhtcpcp.middleware.HTCPCPMiddleware",
]
```

Adding `"djhtcpcp"` to `INSTALLED_APPS` is optional.

The middleware works under both WSGI and ASGI.

## Configuration

By default `/coffee/black/` and `/coffee/espresso/` are coffee pots. Override
them with:

```python
HTCPCP_COFFEE_PATHS = ["/kitchen/pot-1/", "/kitchen/pot-2/"]
```

## Try it

```bash
curl -i -X BREW http://localhost:8000/coffee/black/
curl -i -X BREW http://localhost:8000/tea/earl-grey/
```

## Development

```bash
uv run pytest
uv run ruff check .
```
