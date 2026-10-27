# Changelog

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
