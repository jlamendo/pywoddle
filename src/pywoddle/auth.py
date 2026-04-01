"""Authentication for the Woddle API."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import aiohttp

from .const import TOKEN_REFRESH_HOURS, WODDLE_API_V1
from .exceptions import WoddleAuthError

_LOGGER = logging.getLogger(__name__)


class WoddleAuth:
    """Handles authentication with the Woddle backend.

    The Woddle backend uses its own JWT-based auth (not Firebase).
    Login returns a JWT token and a session cookie.
    """

    def __init__(
        self,
        email: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize auth.

        Args:
            email: Woddle account email.
            password: Woddle account password.
            session: Optional aiohttp session. If not provided, one will be created.
        """
        self.email = email
        self.password = password
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._token_expiry: datetime | None = None
        self._session_cookie: str | None = None
        self._session = session
        self._owns_session = session is None

    @property
    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self._token or not self._token_expiry:
            return False
        return datetime.now(timezone.utc) < self._token_expiry - timedelta(minutes=5)

    @property
    def token(self) -> str | None:
        """Return the current JWT token."""
        return self._token

    @property
    def session_cookie(self) -> str | None:
        """Return the current session cookie."""
        return self._session_cookie

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def authenticate(self) -> None:
        """Authenticate with email/password and obtain a JWT token."""
        session = await self.get_session()

        try:
            async with session.post(
                f"{WODDLE_API_V1}/login",
                json={"email": self.email, "password": self.password},
            ) as resp:
                if resp.status != 200:
                    try:
                        body = await resp.json()
                        error_msg = body.get("message", f"HTTP {resp.status}")
                    except Exception:
                        error_msg = f"HTTP {resp.status}"
                    raise WoddleAuthError(f"Login failed: {error_msg}")

                data = await resp.json()

                if data.get("status") != 200 or "token" not in data:
                    raise WoddleAuthError(
                        f"Login failed: {data.get('message', 'No token returned')}"
                    )

                self._token = data["token"]
                self._refresh_token = data.get("refreshToken")
                self._token_expiry = datetime.now(timezone.utc) + timedelta(
                    hours=TOKEN_REFRESH_HOURS
                )

                if "connect.sid" in resp.cookies:
                    self._session_cookie = resp.cookies["connect.sid"].value

        except aiohttp.ClientError as err:
            raise WoddleAuthError(f"Connection error: {err}") from err

        _LOGGER.debug("Authenticated successfully as %s", self.email)

    async def ensure_valid_token(self) -> None:
        """Ensure we have a valid token, re-authenticating if needed."""
        if not self.is_token_valid:
            await self.authenticate()

    def get_headers(self) -> dict[str, str]:
        """Build request headers with current auth credentials."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if self._session_cookie:
            headers["Cookie"] = f"connect.sid={self._session_cookie}"
        return headers

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()
