# Changelog

## 0.4.0 — 2026-10-27

Full RFC 2324 and RFC 7168 support.

- **Accept-Additions**: parsed with `q` values against the full RFC vocabulary,
  including RFC 7168 sugars. Unavailable additions get `406 Not Acceptable`
  with the list of available ones.
- **start/stop**: `message/coffeepot` bodies are honoured, and brewing state is
  kept in the Django cache. Stopping an idle pot gets `409 Conflict`.
- **POST** with `message/coffeepot`, `application/coffee-pot-command` or
  `message/teapot` is treated as BREW. Other POSTs pass through.
- **Safe** response header: `if-user-awake` for BREW, `yes` for PROPFIND.
- **PROPFIND** on pots returns WebDAV `207 Multi-Status` metadata: type,
  additions, varieties, brewing state, elapsed time and strength.
- **Teapots (RFC 7168)**: varieties with steeping times, `300 Multiple Choices`
  with an `Alternates` header, tea strength (negative after state inversion),
  `403 Forbidden` for configured blasphemous additions, `418` for coffee
  requests, and teapots that can also brew coffee.
- **coffee: URIs**: `djhtcpcp.uri` parses and builds all 23 international
  coffee schemes, including the RFC's mis-encoded French one.
- **Signals** `brew_started`, `brew_stopped` and `when_said` for wiring up
  hardware.
- **Test clients** `HTCPCPClient` and `AsyncHTCPCPClient`.
- **System check** `djhtcpcp.E001` validates `HTCPCP_POTS` when the app is
  installed.
- New `HTCPCP_POTS` setting. `HTCPCP_COFFEE_PATHS` still works.
- Behaviour changes: BREW without milk now says "Brewing coffee." (it says
  "Say WHEN" only once milk is involved), error responses are `text/plain`, and
  `HTCPCPMiddleware.coffee_list` / `coffee_methods` are gone.

## 0.3.0 — 2026-10-27

- Modernized packaging: `pyproject.toml` with hatchling, replacing
  `distutils`/`setup.py` (which no longer works on Python 3.12+) and the
  `pypandoc` build dependency.
- Requires Python 3.10+ and Django 4.2+. Dropped support for Django < 4.2 and
  `MIDDLEWARE_CLASSES`.
- `BREW` to a coffee pot now returns `202 Accepted` instead of `100 Continue`.
  A 1xx status cannot carry a body and broke real HTTP clients and servers.
- Coffee pot responses use the `message/coffeepot` content type.
- New `HTCPCP_COFFEE_PATHS` setting to configure which paths are coffee pots.
- Added an MIT license, a test suite and CI.
- Releases are published to PyPI via trusted publishing.

## 0.2.7 — 2017-05-26

- Last release of the legacy line.
