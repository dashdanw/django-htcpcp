"""Brewing state, kept in the Django cache so it is shared between workers."""

import hashlib
import time
from dataclasses import asdict, dataclass

from django.conf import settings
from django.core.cache import caches

_TIMEOUT = 24 * 60 * 60


@dataclass
class Brew:
    started: float
    additions: list
    variety: str | None = None

    @property
    def elapsed(self):
        return max(0.0, time.time() - self.started)


def _cache():
    return caches[getattr(settings, "HTCPCP_CACHE", "default")]


def _key(pot, variety):
    digest = hashlib.sha256(f"{pot.path}\0{variety or ''}".encode()).hexdigest()
    return f"djhtcpcp:brew:{digest}"


def start(pot, variety, additions):
    brew = Brew(time.time(), [a.name for a in additions], variety)
    _cache().set(_key(pot, variety), asdict(brew), _TIMEOUT)
    return brew


def get(pot, variety):
    data = _cache().get(_key(pot, variety))
    return Brew(**data) if data else None


def stop(pot, variety):
    brew = get(pot, variety)
    if brew is not None:
        _cache().delete(_key(pot, variety))
    return brew


def strength(elapsed, steep_seconds):
    """Tea strength as a percentage of the variety's recommended strength.

    Strength grows with steeping time. Left far too long, the proportion of tea
    to water inverts and the pot reports a negative strength (RFC 7168 2.1.2).
    """
    percent = round(100 * elapsed / steep_seconds)
    return -percent if elapsed > 2 * steep_seconds else percent
