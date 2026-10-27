"""RFC 7168: HTCPCP-TEA."""

from unittest import mock
from xml.etree import ElementTree as ET

from djhtcpcp import state

NS = {"D": "DAV:", "C": "urn:ietf:rfc:2324"}


def test_root_offers_alternates(teapots, htcpcp):
    response = htcpcp.brew("/pot-0/", tea=True)
    assert response.status_code == 300
    assert response["Alternates"] == (
        '{"/pot-0/darjeeling/" {type message/teapot}}, {"/pot-0/earl-grey/" {type message/teapot}}'
    )


def test_coffee_to_teapot(teapots, htcpcp):
    response = htcpcp.brew("/pot-0/")
    assert response.status_code == 418
    assert "darjeeling" in response["Alternates"]
    assert htcpcp.brew("/pot-0/earl-grey/").status_code == 418


def test_coffee_capable_teapot(teapots, htcpcp):
    response = htcpcp.brew("/pot-1/")
    assert response.status_code == 202
    assert response["Alternates"].startswith('{"/pot-1/" {type message/coffeepot}}')


def test_brew_tea_and_strength(teapots, htcpcp):
    with mock.patch("djhtcpcp.state.time.time", return_value=1000):
        response = htcpcp.brew("/pot-0/darjeeling/", tea=True)
    assert response.status_code == 202
    assert response["Content-Type"] == "message/teapot"

    with mock.patch("djhtcpcp.state.time.time", return_value=1090):
        prop = ET.fromstring(htcpcp.propfind("/pot-0/darjeeling/").content)
        assert prop.findtext(".//C:strength", namespaces=NS) == "50"
        response = htcpcp.brew("/pot-0/darjeeling/", "stop", tea=True)
    assert response.content == b"Stopped brewing darjeeling. Served at 50% strength."


def test_state_inversion():
    assert state.strength(180, 180) == 100
    assert state.strength(360, 180) == 200
    assert state.strength(361, 180) == -201


def test_forbidden_combination(teapots, htcpcp):
    response = htcpcp.brew("/pot-0/darjeeling/", tea=True, additions=["Whisky"])
    assert response.status_code == 403
    assert htcpcp.brew("/pot-0/earl-grey/", tea=True, additions=["Whisky"]).status_code == 202


def test_sugar_additions(teapots, htcpcp):
    response = htcpcp.brew("/pot-0/earl-grey/", tea=True, additions=["Stevia", "Xylitol"])
    assert response.status_code == 202


def test_unknown_variety(teapots, htcpcp):
    response = htcpcp.brew("/pot-0/rooibos/", tea=True)
    assert response.status_code == 404
    assert "Alternates" in response


def test_when_tea(teapots, htcpcp):
    assert htcpcp.when("/pot-0/darjeeling/").content == b"Mmmmmmm tea!"
    assert htcpcp.when("/pot-0/").status_code == 418
    assert htcpcp.when("/pot-1/").status_code == 201


def test_teapot_propfind_lists_varieties(teapots, htcpcp):
    root = ET.fromstring(htcpcp.propfind("/pot-0/").content)
    varieties = root.findall(".//C:varieties/C:variety", NS)
    assert [(v.text, v.get("steep-seconds")) for v in varieties] == [
        ("darjeeling", "180"),
        ("earl-grey", "240"),
    ]
