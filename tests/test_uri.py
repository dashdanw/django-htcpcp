import pytest

from djhtcpcp.uri import COFFEE_SCHEMES, parse_coffee_uri


def test_parse():
    uri = parse_coffee_uri("koffie://kitchen/pot-1?Cream,vanilla")
    assert uri.languages == ("Afrikaans", "Dutch")
    assert (uri.host, uri.pot) == ("kitchen", 1)
    assert [a.name for a in uri.additions] == ["Cream", "Vanilla"]
    assert str(uri) == "koffie://kitchen/pot-1?Cream,Vanilla"


@pytest.mark.parametrize("scheme", list(COFFEE_SCHEMES))
def test_every_scheme(scheme):
    assert parse_coffee_uri(f"{scheme}:").scheme == scheme


@pytest.mark.parametrize("word", ["café", "caf%C3%E8", "COFFEE", "кофе", "Kaffee", "%4Baffee"])
def test_spellings(word):
    assert parse_coffee_uri(f"{word}://host").host == "host"


@pytest.mark.parametrize("uri", ["kaffee://host", "tea://host", "coffee://host/kettle", "coffee"])
def test_not_coffee(uri):
    with pytest.raises(ValueError):
        parse_coffee_uri(uri)
