"""RFC 2324: BREW/POST, Accept-Additions, Safe, start/stop, PROPFIND."""

from xml.etree import ElementTree as ET

import pytest

from djhtcpcp import signals
from djhtcpcp.additions import parse_accept_additions

NS = {"D": "DAV:", "C": "urn:ietf:rfc:2324"}


def test_brew_is_conditionally_safe(htcpcp):
    response = htcpcp.brew("/coffee/black/")
    assert response.status_code == 202
    assert response["Safe"] == "if-user-awake"
    assert response.content == b"Brewing coffee."


def test_milk_means_say_when(htcpcp):
    response = htcpcp.brew("/coffee/black/", additions=["Cream"])
    assert response.content == b"Say WHEN . . . "


@pytest.mark.parametrize("content_type", ["message/coffeepot", "application/coffee-pot-command"])
def test_post_with_htcpcp_media_type_is_brew(htcpcp, content_type):
    response = htcpcp.post("/coffee/black/", "start", content_type=content_type)
    assert response.status_code == 202


def test_ordinary_post_passes_through(htcpcp):
    assert htcpcp.post("/coffee/black/", {"a": 1}).content == b"a regular view"


def test_stop(htcpcp):
    assert htcpcp.brew("/coffee/black/", "stop").status_code == 409
    htcpcp.brew("/coffee/black/")
    response = htcpcp.brew("/coffee/black/", "stop")
    assert response.status_code == 200
    assert response.content == b"Stopped brewing coffee."
    assert htcpcp.brew("/coffee/black/", "stop").status_code == 409


def test_bad_message_body(htcpcp):
    assert htcpcp.brew("/coffee/black/", "decaf").status_code == 400


def test_unavailable_additions_are_not_acceptable(settings, htcpcp):
    settings.HTCPCP_POTS = {"/coffee/black/": {"additions": ["Cream", "Vanilla"]}}
    response = htcpcp.brew("/coffee/black/", additions=["cream", "Rum"])
    assert response.status_code == 406
    assert response.content == b"Cannot provide Rum. Available additions: Cream, Vanilla."
    assert htcpcp.brew("/coffee/black/", additions=["*", "Rum;q=0"]).status_code == 202


def test_pot_without_additions(teapots, htcpcp):
    response = htcpcp.brew("/coffee/plain/", additions=["Cream"])
    assert response.status_code == 406
    assert response.content == b"This pot cannot provide additions."


def test_tea_to_coffee_pot(htcpcp):
    assert htcpcp.brew("/coffee/black/", tea=True).status_code == 415


def test_propfind(htcpcp):
    htcpcp.brew("/coffee/black/", additions=["Whisky"])
    response = htcpcp.propfind("/coffee/black/")
    assert response.status_code == 207
    assert response["Safe"] == "yes"
    prop = ET.fromstring(response.content).find("D:response/D:propstat/D:prop", NS)
    assert prop.findtext("C:pot-type", namespaces=NS) == "coffeepot"
    assert prop.findtext("C:brewing", namespaces=NS) == "true"
    assert prop.findtext("C:brewing-addition", namespaces=NS) == "Whisky"
    assert "Aquavit" in [a.text for a in prop.findall("C:additions/C:addition", NS)]


def test_propfind_elsewhere_passes_through(htcpcp):
    assert htcpcp.propfind("/coffee/black").status_code == 404


def test_signals(htcpcp):
    events = []

    def record(sender, signal, **kwargs):
        events.append((signal, kwargs["pot"].path))

    for signal in (signals.brew_started, signals.brew_stopped, signals.when_said):
        signal.connect(record, weak=False)
    try:
        htcpcp.brew("/coffee/black/")
        htcpcp.when("/coffee/black/")
        htcpcp.brew("/coffee/black/", "stop")
    finally:
        for signal in (signals.brew_started, signals.brew_stopped, signals.when_said):
            signal.disconnect(record)
    assert [e[0] for e in events] == [signals.brew_started, signals.when_said, signals.brew_stopped]


def test_parse_accept_additions():
    parsed = parse_accept_additions("whole-milk;q=0.5, Cinnamon, Rum;q=0, *")
    assert [(a.name, a.category) for a in parsed] == [
        ("Whole-milk", "milk"),
        ("Cinnamon", None),
        ("*", None),
    ]
    assert parsed[0].params == {"q": "0.5"}
