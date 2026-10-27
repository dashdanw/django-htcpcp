import pytest
from django.core.exceptions import ImproperlyConfigured

from djhtcpcp.checks import check_pots
from djhtcpcp.pots import get_pots


@pytest.mark.parametrize(
    "config",
    [
        {"coffee/": {}},
        {"/a/": {"type": "kettle"}},
        {"/a/": {"type": "coffee", "varieties": ["x"]}},
        {"/a/": {"type": "tea", "varieties": {"x": 0}}},
        {"/a/": {"type": "tea", "varieties": ["x"], "forbidden_additions": {"y": ["Rum"]}}},
        {"/a/": {"additions": "Cream"}},
    ],
)
def test_invalid_config(settings, config):
    settings.HTCPCP_POTS = config
    with pytest.raises(ImproperlyConfigured):
        get_pots()
    assert [e.id for e in check_pots(None)] == ["djhtcpcp.E001"]


def test_legacy_coffee_paths(settings):
    settings.HTCPCP_COFFEE_PATHS = ["/pot/"]
    assert list(get_pots()) == ["/pot/"]
    assert check_pots(None) == []
