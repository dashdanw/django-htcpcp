"""Pot configuration, read from the ``HTCPCP_POTS`` setting."""

from dataclasses import dataclass, field

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .additions import addition
from .rfc import ALL_ADDITIONS, DEFAULT_STEEP_SECONDS

COFFEE = "coffee"
TEA = "tea"

DEFAULT_COFFEE_PATHS = ("/coffee/black/", "/coffee/espresso/")

_ALLOWED_KEYS = {
    COFFEE: {"type", "additions"},
    TEA: {"type", "additions", "varieties", "coffee", "forbidden_additions"},
}


@dataclass(frozen=True)
class Pot:
    path: str
    type: str = COFFEE
    additions: tuple = ALL_ADDITIONS
    #: Tea variety name -> recommended steeping time in seconds.
    varieties: dict = field(default_factory=dict)
    #: Whether a teapot can also brew coffee (RFC 7168 section 4).
    coffee: bool = True
    #: Tea variety name -> additions deemed contrary to the sensibilities of drinkers.
    forbidden_additions: dict = field(default_factory=dict)

    @property
    def is_teapot(self):
        return self.type == TEA

    def variety_path(self, variety):
        return f"{self.path.rstrip('/')}/{variety}{'/' if self.path.endswith('/') else ''}"

    def resolve(self, path):
        """Return ``(matched, variety)`` for a request path."""
        if path == self.path:
            return True, None
        if self.is_teapot:
            prefix = self.path.rstrip("/") + "/"
            rest = path[len(prefix) :] if path.startswith(prefix) else ""
            if self.path.endswith("/"):
                if not rest.endswith("/"):
                    return False, None
                rest = rest[:-1]
            if rest and "/" not in rest:
                return True, rest
        return False, None


def _additions(value, where):
    if not isinstance(value, list | tuple):
        raise ImproperlyConfigured(f"{where} must be a list of addition names.")
    return tuple(addition(str(name)).name for name in value)


def _pot(path, options):
    where = f"HTCPCP_POTS[{path!r}]"
    if not isinstance(path, str) or not path.startswith("/"):
        raise ImproperlyConfigured(f"{where}: pot paths must start with '/'.")
    if not isinstance(options, dict):
        raise ImproperlyConfigured(f"{where} must be a dict.")
    pot_type = options.get("type", COFFEE)
    if pot_type not in _ALLOWED_KEYS:
        raise ImproperlyConfigured(f"{where}['type'] must be 'coffee' or 'tea'.")
    unknown = set(options) - _ALLOWED_KEYS[pot_type]
    if unknown:
        raise ImproperlyConfigured(f"{where}: unknown option(s) {', '.join(sorted(unknown))}.")

    kwargs = {"path": path, "type": pot_type}
    if "additions" in options:
        kwargs["additions"] = _additions(options["additions"], f"{where}['additions']")
    if pot_type == TEA:
        varieties = options.get("varieties", {})
        if isinstance(varieties, list | tuple):
            varieties = dict.fromkeys(varieties, DEFAULT_STEEP_SECONDS)
        if not isinstance(varieties, dict) or not all(
            isinstance(name, str) and name and "/" not in name for name in varieties
        ):
            raise ImproperlyConfigured(
                f"{where}['varieties'] must be a list of names or a dict of name -> seconds."
            )
        if not all(isinstance(s, int | float) and s > 0 for s in varieties.values()):
            raise ImproperlyConfigured(f"{where}['varieties'] steep times must be positive.")
        forbidden = options.get("forbidden_additions", {})
        if not isinstance(forbidden, dict) or set(forbidden) - set(varieties):
            raise ImproperlyConfigured(
                f"{where}['forbidden_additions'] must map configured varieties to additions."
            )
        kwargs["varieties"] = dict(varieties)
        kwargs["coffee"] = bool(options.get("coffee", False))
        kwargs["forbidden_additions"] = {
            variety: _additions(names, f"{where}['forbidden_additions'][{variety!r}]")
            for variety, names in forbidden.items()
        }
    return Pot(**kwargs)


def get_pots():
    """Return the configured pots, keyed by path."""
    config = getattr(settings, "HTCPCP_POTS", None)
    if config is None:
        paths = getattr(settings, "HTCPCP_COFFEE_PATHS", DEFAULT_COFFEE_PATHS)
        config = {path: {"type": COFFEE} for path in paths}
    if not isinstance(config, dict):
        raise ImproperlyConfigured("HTCPCP_POTS must be a dict of path -> options.")
    return {path: _pot(path, options) for path, options in config.items()}


def resolve(path):
    """Find the pot serving ``path``. Returns ``(pot, variety)`` or ``None``."""
    pots = get_pots()
    if path in pots:
        return pots[path], None
    for pot in pots.values():
        matched, variety = pot.resolve(path)
        if matched:
            return pot, variety
    return None
