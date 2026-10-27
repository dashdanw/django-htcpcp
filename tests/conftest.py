import pytest
from django.core.cache import cache

from djhtcpcp.client import HTCPCPClient

TEA_POTS = {
    "/coffee/black/": {"type": "coffee"},
    "/coffee/plain/": {"type": "coffee", "additions": []},
    "/pot-0/": {
        "type": "tea",
        "varieties": {"darjeeling": 180, "earl-grey": 240},
        "forbidden_additions": {"darjeeling": ["Whisky"]},
    },
    "/pot-1/": {"type": "tea", "varieties": ["peppermint"], "coffee": True},
}


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()


@pytest.fixture
def htcpcp():
    return HTCPCPClient()


@pytest.fixture
def teapots(settings):
    settings.HTCPCP_POTS = TEA_POTS
