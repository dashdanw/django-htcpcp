"""The international "coffee" URI scheme (RFC 2324 section 3).

>>> uri = parse_coffee_uri("koffie://kitchen/pot-1?Cream,Vanilla")
>>> uri.languages, uri.host, uri.pot, [a.name for a in uri.additions]
(('Afrikaans', 'Dutch'), 'kitchen', 1, ['Cream', 'Vanilla'])
"""

import re
from dataclasses import dataclass, field
from urllib.parse import quote, unquote

from .additions import Addition, addition

#: Scheme (as written in the RFC, percent-encoded UTF-8) -> languages.
COFFEE_SCHEMES = {
    "koffie": ("Afrikaans", "Dutch"),
    "q%C3%A6hv%C3%A6": ("Azerbaijani",),
    "%D9%82%D9%87%D9%88%D8%A9": ("Arabic",),
    "akeita": ("Basque",),
    "koffee": ("Bengali",),
    "kahva": ("Bosnian",),
    "kafe": ("Bulgarian", "Czech"),
    "caf%C3%A9": ("Catalan", "French", "Galician"),
    "%E5%92%96%E5%95%A1": ("Chinese",),
    "kava": ("Croatian",),
    "k%C3%A1va": ("Czech",),
    "kaffe": ("Danish", "Norwegian", "Swedish"),
    "coffee": ("English",),
    "kafo": ("Esperanto",),
    "kohv": ("Estonian",),
    "kahvi": ("Finnish",),
    "%4Baffee": ("German",),
    "%CE%BA%CE%B1%CF%86%CE%AD": ("Greek",),
    "%E0%A4%95%E0%A5%8C%E0%A4%AB%E0%A5%80": ("Hindi",),
    "%E3%82%B3%E3%83%BC%E3%83%92%E3%83%BC": ("Japanese",),
    "%EC%BB%A4%ED%94%BC": ("Korean",),
    "%D0%BA%D0%BE%D1%84%D0%B5": ("Russian",),
    "%E0%B8%81%E0%B8%B2%E0%B9%81%E0%B8%9F": ("Thai",),
}

#: The RFC spells the French scheme "caf%C3%E8", which is not valid UTF-8.
_ERRATA = {"caf%C3%E8": "caf%C3%A9"}

#: Capitalization is important for German, so "Kaffee" is matched exactly.
_CASE_SENSITIVE = {"Kaffee"}

_BY_WORD = {unquote(scheme): scheme for scheme in COFFEE_SCHEMES}
_POT = re.compile(r"pot-(\d+)")


@dataclass(frozen=True)
class CoffeeURI:
    scheme: str
    host: str | None = None
    pot: int | None = None
    additions: tuple[Addition, ...] = field(default=())

    @property
    def languages(self):
        return COFFEE_SCHEMES[self.scheme]

    def __str__(self):
        uri = f"{self.scheme}:"
        if self.host is not None:
            uri += f"//{self.host}"
        if self.pot is not None:
            uri += f"/pot-{self.pot}"
        if self.additions:
            uri += "?" + ",".join(quote(a.name) for a in self.additions)
        return uri


def coffee_scheme(word):
    """Return the canonical scheme for a word for "coffee", or None if it is not one."""
    word = unquote(_ERRATA.get(word, word))
    if word in _CASE_SENSITIVE:
        return _BY_WORD[word]
    for candidate, scheme in _BY_WORD.items():
        if candidate not in _CASE_SENSITIVE and candidate.casefold() == word.casefold():
            return scheme
    return None


def parse_coffee_uri(uri):
    """Parse a coffee URI. Raises ValueError if it is not one."""
    word, sep, rest = uri.partition(":")
    scheme = coffee_scheme(word) if sep else None
    if scheme is None:
        raise ValueError(f"{uri!r} is not a coffee URI.")

    rest, _, query = rest.partition("?")
    host = None
    if rest.startswith("//"):
        host, slash, rest = rest[2:].partition("/")
        rest = slash + rest
    pot = None
    if rest not in ("", "/"):
        designator = _POT.fullmatch(rest.lstrip("/"))
        if designator is None:
            raise ValueError(f"{rest!r} is not a pot designator (expected pot-<integer>).")
        pot = int(designator.group(1))
    additions = tuple(addition(unquote(a.strip())) for a in query.split(",") if a.strip())
    return CoffeeURI(scheme, host or None, pot, additions)
