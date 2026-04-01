"""Async client for the Woddle REST API."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .auth import WoddleAuth
from .const import WODDLE_ACTIVITY_BASE, WODDLE_API_V1
from .exceptions import WoddleApiError, WoddleAuthError
from .models import (
    WoddleActivity,
    WoddleBaby,
    WoddleDevice,
    WoddleUserProfile,
)

_LOGGER = logging.getLogger(__name__)


class WoddleClient:
    """Async client for the Woddle API.

    All API-specific logic lives here. Home Assistant integration code
    should interact only with this client and its model objects.
    """

    def __init__(self, auth: WoddleAuth) -> None:
        """Initialize the client.

        Args:
            auth: Authenticated WoddleAuth instance.
        """
        self.auth = auth

    async def _request(
        self,
        method: str,
        url: str,
        json: dict | None = None,
    ) -> Any:
        """Make an authenticated API request.

        Handles 401 by re-authenticating and retrying once.
        """
        await self.auth.ensure_valid_token()
        session = await self.auth.get_session()
        headers = self.auth.get_headers()

        try:
            async with session.request(
                method, url, headers=headers, json=json
            ) as resp:
                if resp.status == 401:
                    await self.auth.authenticate()
                    headers = self.auth.get_headers()
                    async with session.request(
                        method, url, headers=headers, json=json
                    ) as retry_resp:
                        return await self._handle_response(retry_resp)
                return await self._handle_response(resp)

        except aiohttp.ClientError as err:
            raise WoddleApiError(f"Connection error: {err}") from err

    @staticmethod
    async def _handle_response(resp: aiohttp.ClientResponse) -> Any:
        """Parse and validate an API response."""
        if resp.status >= 400:
            text = await resp.text()
            raise WoddleApiError(
                f"API error {resp.status}: {text[:200]}",
                status_code=resp.status,
            )
        text = await resp.text()
        if not text:
            return {}
        return await resp.json(content_type=None)

    # ── Baby endpoints ──────────────────────────────────────────────

    async def fetch_babies(self) -> list[WoddleBaby]:
        """Fetch all babies on the account."""
        data = await self._request("GET", f"{WODDLE_API_V1}/baby/fetchBabies")
        raw_babies = data.get("babies", []) if isinstance(data, dict) else []
        return [WoddleBaby.from_api(b) for b in raw_babies]

    async def fetch_baby_details(self, baby_id: str) -> WoddleBaby:
        """Fetch details for a specific baby."""
        data = await self._request("GET", f"{WODDLE_API_V1}/baby/get/{baby_id}")
        raw = data.get("data", {}) if isinstance(data, dict) else {}
        return WoddleBaby.from_api(raw)

    # ── User endpoints ──────────────────────────────────────────────

    async def fetch_user_profile(self) -> WoddleUserProfile:
        """Fetch user profile."""
        data = await self._request("GET", f"{WODDLE_API_V1}/user/details")
        details = data.get("details", {}) if isinstance(data, dict) else {}
        return WoddleUserProfile.from_api(details)

    # ── Activity endpoints ──────────────────────────────────────────

    async def fetch_recent_activities(self) -> list[WoddleActivity]:
        """Fetch recent activities from the user profile.

        The /api/v1/user/profile endpoint returns the most recent
        activities across all babies. This is the primary polling method.
        """
        data = await self._request("GET", f"{WODDLE_API_V1}/user/profile")
        details = data.get("details", {}) if isinstance(data, dict) else {}
        raw_activities = details.get("activities", [])
        return [WoddleActivity.from_api(a) for a in raw_activities]

    # ── Device endpoints ────────────────────────────────────────────

    async def fetch_devices(self) -> list[WoddleDevice]:
        """Fetch registered Woddle devices."""
        data = await self._request(
            "GET", f"{WODDLE_ACTIVITY_BASE}/device/fetchDevices"
        )
        raw_devices = data.get("data", []) if isinstance(data, dict) else []
        return [WoddleDevice.from_api(d) for d in raw_devices]

    # ── Lifecycle ───────────────────────────────────────────────────

    async def close(self) -> None:
        """Close the underlying auth session."""
        await self.auth.close()
