# django-htcpcp

[![PyPI](https://img.shields.io/pypi/v/django-htcpcp.svg)](https://pypi.org/project/django-htcpcp/)
[![CI](https://github.com/dashdanw/django-htcpcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dashdanw/django-htcpcp/actions/workflows/ci.yml)

Django middleware implementing the HyperText Coffee Pot Control Protocol
(HTCPCP), as specified in [RFC 2324](https://www.rfc-editor.org/rfc/rfc2324)
and extended by [RFC 7168](https://www.rfc-editor.org/rfc/rfc7168).

Coffee pots (RFC 2324):

| Request                                   | Response                                     |
| ----------------------------------------- | -------------------------------------------- |
| `BREW` (or `POST` with an HTCPCP type)    | `202 Accepted`, `Safe: if-user-awake`        |
| `BREW` with body `stop`                   | `200 OK`, or `409 Conflict` if not brewing   |
| `BREW` with unavailable `Accept-Additions`| `406 Not Acceptable` listing what's on offer |
| `WHEN`                                    | `201 Created` — "Mmmmmmm coffee!"            |
| `PROPFIND`                                | `207 Multi-Status` with pot metadata         |

Teapots (RFC 7168):

| Request                                       | Response                                   |
| --------------------------------------------- | ------------------------------------------ |
| `BREW` `message/teapot` to the pot            | `300 Multiple Choices` + `Alternates`      |
| `BREW` `message/teapot` to `<pot>/<variety>/` | `202 Accepted`; `stop` reports strength    |
| `BREW` for coffee                             | `418 I'm a teapot` (unless `coffee: True`) |
| Additions contrary to good taste              | `403 Forbidden`                            |

`BREW` or `WHEN` to anything that isn't a pot gets `418 I'm a teapot`. Everything
else (including `GET`, ordinary `POST`s and `PROPFIND` outside pots) is passed
through untouched, so the middleware is safe to drop into an existing site.

## Requirements

- Python 3.10+
- Django 4.2+

## Installation

```bash
pip install django-htcpcp
```

```python
INSTALLED_APPS = [
    # ...
    "djhtcpcp",  # optional, enables system checks for HTCPCP_POTS
]

MIDDLEWARE = [
    # ...
    "djhtcpcp.middleware.HTCPCPMiddleware",
]
```

The middleware works under both WSGI and ASGI.

## Configuration

By default `/coffee/black/` and `/coffee/espresso/` are coffee pots offering every
addition in the RFCs. Configure your own pots with `HTCPCP_POTS`:

```python
HTCPCP_POTS = {
    "/coffee/black/": {"type": "coffee"},
    # "In practice, most automated coffee pots cannot currently provide additions."
    "/coffee/office/": {"type": "coffee", "additions": []},
    "/pot-0/": {
        "type": "tea",
        # Variety -> recommended steeping time in seconds (or a plain list for 180s).
        "varieties": {"darjeeling": 180, "earl-grey": 240, "peppermint": 300},
        "forbidden_additions": {"darjeeling": ["Whisky", "Raspberry"]},
        "coffee": False,  # a teapot that also brews coffee would set True
        "additions": ["Whole-milk", "Sugar", "Stevia"],
    },
}
```

Additions are the RFC vocabulary: milk (`Cream`, `Half-and-half`, `Whole-milk`,
`Part-Skim`, `Skim`, `Non-Dairy`), syrup (`Vanilla`, `Almond`, `Raspberry`,
`Chocolate`), alcohol (`Whisky`, `Rum`, `Kahlua`, `Aquavit`) and sugar (`Sugar`,
`Xylitol`, `Stevia`). The RFC leaves sweeteners and spices to you, so any other
name you list (`"Cinnamon"`) works too. Matching is case-insensitive and
`q=0` entries are ignored.

Brewing state lives in the Django cache (set `HTCPCP_CACHE` to use a cache other
than `"default"`). Use a shared cache such as Redis in production so every worker
sees the same pot. Tea strength is measured from `start` to `stop` against the
variety's steeping time; leave it brewing for more than twice that and the pot
reports a negative strength, per RFC 7168's warning about state inversion.

`HTCPCP_COFFEE_PATHS` from 0.3.0 is still honoured when `HTCPCP_POTS` is unset.

## Try it

```bash
curl -i -X BREW -H "Accept-Additions: Cream" http://localhost:8000/coffee/black/
curl -i -X BREW -H "Content-Type: message/teapot" http://localhost:8000/pot-0/
curl -i -X BREW -H "Content-Type: message/teapot" -d start http://localhost:8000/pot-0/darjeeling/
curl -i -X BREW -H "Content-Type: message/teapot" -d stop http://localhost:8000/pot-0/darjeeling/
curl -i -X PROPFIND http://localhost:8000/pot-0/darjeeling/
```

## Connecting hardware

Signals in `djhtcpcp.signals` fire for every pot action, each with `request`, `pot`
and `variety`:

```python
from django.dispatch import receiver
from djhtcpcp.signals import brew_started, brew_stopped, when_said


@receiver(brew_started)
def switch_on(sender, pot, variety, additions, **kwargs):
    gpio.on(pot.path)
```

`brew_stopped` also carries `elapsed` and `strength`.

## Testing your pots

```python
from djhtcpcp.client import HTCPCPClient  # or AsyncHTCPCPClient

client = HTCPCPClient()
client.brew("/coffee/black/", additions=["Cream"])
client.brew("/pot-0/darjeeling/", "stop", tea=True)
client.when("/coffee/black/")
client.propfind("/pot-0/")
```

## The coffee URI scheme

All 23 international `coffee:` schemes from RFC 2324 section 3 can be parsed and built:

```python
>>> from djhtcpcp.uri import parse_coffee_uri
>>> uri = parse_coffee_uri("café://kitchen/pot-1?Cream,Vanilla")
>>> uri.languages, uri.host, uri.pot
(('Catalan', 'French', 'Galician'), 'kitchen', 1)
```

German is case-sensitive: `Kaffee:` is coffee, `kaffee:` is not.

## Development

```bash
uv run pytest
uv run ruff check .
```
