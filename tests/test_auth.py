"""Tests for pywoddle.auth."""

import pytest
from aioresponses import aioresponses

from pywoddle import WoddleAuth
from pywoddle.const import WODDLE_API_V1
from pywoddle.exceptions import WoddleAuthError


@pytest.mark.asyncio
async def test_authenticate_success(login_response):
    """Test successful authentication."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()

        assert auth.is_token_valid
        assert auth.token is not None
        assert auth.token.startswith("eyJ")

        await auth.close()


@pytest.mark.asyncio
async def test_authenticate_invalid_credentials():
    """Test authentication with wrong credentials."""
    with aioresponses() as mock:
        mock.post(
            f"{WODDLE_API_V1}/login",
            payload={"status": 400, "message": "Invalid credentials"},
            status=400,
        )

        auth = WoddleAuth(email="bad@example.com", password="wrong")
        with pytest.raises(WoddleAuthError, match="Login failed"):
            await auth.authenticate()

        await auth.close()


@pytest.mark.asyncio
async def test_authenticate_no_token_in_response():
    """Test authentication when response has no token."""
    with aioresponses() as mock:
        mock.post(
            f"{WODDLE_API_V1}/login",
            payload={"status": 200},
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        with pytest.raises(WoddleAuthError, match="No token returned"):
            await auth.authenticate()

        await auth.close()


@pytest.mark.asyncio
async def test_authenticate_connection_error():
    """Test authentication with connection failure."""
    import aiohttp as _aiohttp

    with aioresponses() as mock:
        mock.post(
            f"{WODDLE_API_V1}/login",
            exception=_aiohttp.ClientConnectionError("Connection refused"),
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        with pytest.raises(WoddleAuthError, match="Connection error"):
            await auth.authenticate()

        await auth.close()


@pytest.mark.asyncio
async def test_ensure_valid_token_refreshes(login_response):
    """Test that ensure_valid_token re-authenticates when expired."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        assert not auth.is_token_valid

        await auth.ensure_valid_token()
        assert auth.is_token_valid

        await auth.close()


@pytest.mark.asyncio
async def test_get_headers(login_response):
    """Test header generation after auth."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()

        headers = auth.get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer eyJ")
        assert headers["Content-Type"] == "application/json"

        await auth.close()


@pytest.mark.asyncio
async def test_session_management():
    """Test that close() cleans up the session."""
    auth = WoddleAuth(email="test@example.com", password="testpass")
    session = await auth.get_session()
    assert not session.closed

    await auth.close()
    assert session.closed


@pytest.mark.asyncio
async def test_external_session_not_closed():
    """Test that an externally provided session is not closed."""
    import aiohttp

    external_session = aiohttp.ClientSession()
    auth = WoddleAuth(
        email="test@example.com", password="testpass", session=external_session
    )

    await auth.close()
    assert not external_session.closed

    await external_session.close()
