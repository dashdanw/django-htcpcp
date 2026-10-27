"""Parsing for the Accept-Additions request header (RFC 2324 section 2.2.2.1)."""

from dataclasses import dataclass, field

from .rfc import ADDITIONS

_CANONICAL = {
    name.casefold(): (name, category) for category, names in ADDITIONS.items() for name in names
}


@dataclass(frozen=True)
class Addition:
    name: str
    category: str | None = None
    params: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def is_wildcard(self):
        return self.name == "*"

    @property
    def is_milk(self):
        return self.category == "milk"


def addition(name, params=None):
    """Build an Addition, normalizing the name to its RFC spelling when it has one."""
    canonical, category = _CANONICAL.get(name.casefold(), (name, None))
    return Addition(canonical, category, params or {})


def parse_accept_additions(value):
    """Parse an Accept-Additions header value into a list of Additions.

    Additions with ``q=0`` are not acceptable to the client and are dropped.
    """
    result = []
    for item in (value or "").split(","):
        name, *raw_params = (part.strip() for part in item.split(";"))
        if not name:
            continue
        params = {}
        for param in raw_params:
            key, _, val = param.partition("=")
            params[key.strip().casefold()] = val.strip().strip('"')
        try:
            if float(params.get("q", 1)) <= 0:
                continue
        except ValueError:
            pass
        result.append(addition(name, params))
    return result
