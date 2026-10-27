import pytest
from django.test import AsyncClient, Client


@pytest.fixture
def client():
    return Client()


@pytest.mark.parametrize("path", ["/coffee/black/", "/coffee/espresso/"])
def test_brew_coffee(client, path):
    response = client.generic("BREW", path)
    assert response.status_code == 202
    assert response["Content-Type"] == "message/coffeepot"


@pytest.mark.parametrize("path", ["/coffee/black/", "/coffee/espresso/"])
def test_when_coffee(client, path):
    response = client.generic("WHEN", path)
    assert response.status_code == 201
    assert response.content == b"Mmmmmmm coffee!"


@pytest.mark.parametrize("method", ["BREW", "WHEN"])
@pytest.mark.parametrize("path", ["/", "/tea/earl-grey/", "/coffee/black"])
def test_teapot(client, method, path):
    response = client.generic(method, path)
    assert response.status_code == 418
    assert response.content == b"I'm a teapot."


def test_regular_requests_pass_through(client):
    assert client.get("/coffee/black/").content == b"a regular view"
    assert client.get("/nowhere/").status_code == 404


def test_custom_coffee_paths(client, settings):
    settings.HTCPCP_COFFEE_PATHS = ["/pot-1/"]
    assert client.generic("BREW", "/pot-1/").status_code == 202
    assert client.generic("BREW", "/coffee/black/").status_code == 418


async def test_async_stack():
    response = await AsyncClient().generic("BREW", "/coffee/espresso/")
    assert response.status_code == 202
