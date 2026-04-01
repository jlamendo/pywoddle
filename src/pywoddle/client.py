"""Async client for the Woddle REST API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from .auth import WoddleAuth
from .const import WODDLE_ACTIVITY_BASE, WODDLE_API_V1
from .exceptions import WoddleApiError
from .models import (
    WoddleActivity,
    WoddleBaby,
    WoddleDashboard,
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
        self.auth = auth

    async def _request(
        self, method: str, url: str, json: dict | None = None,
    ) -> Any:
        """Make an authenticated API request with 401 retry."""
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

    # ── Dashboard & Activities ──────────────────────────────────────

    async def fetch_dashboard(self, baby_id: str) -> WoddleDashboard:
        """Fetch the dashboard for a baby.

        Returns latest activity per type with activity_type_ids.
        """
        data = await self._request(
            "GET", f"{WODDLE_ACTIVITY_BASE}/dashboard/{baby_id}"
        )
        return WoddleDashboard.from_api(data)

    async def fetch_calendar(
        self,
        baby_id: str,
        date: str | None = None,
        tz: str = "America/Los_Angeles",
    ) -> list[WoddleActivity]:
        """Fetch all activities for a day with full details.

        Args:
            baby_id: Baby UUID.
            date: Date string (YYYY-MM-DD). Defaults to today.
            tz: Timezone name.
        """
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = await self._request(
            "GET",
            f"{WODDLE_ACTIVITY_BASE}/dashboard/{baby_id}/calendar"
            f"?date={date}&timezone={tz}",
        )
        raw = data.get("activities", []) if isinstance(data, dict) else []
        return [WoddleActivity.from_api(a) for a in raw]

    async def fetch_history(
        self, baby_id: str, activity_type_id: str
    ) -> list[WoddleActivity]:
        """Fetch activity history for a specific activity type.

        Args:
            baby_id: Baby UUID.
            activity_type_id: UUID of the activity type (from dashboard).
        """
        data = await self._request(
            "GET",
            f"{WODDLE_ACTIVITY_BASE}/fetchHistory/{baby_id}/{activity_type_id}",
        )
        raw = data.get("activities", []) if isinstance(data, dict) else []
        return [WoddleActivity.from_api(a) for a in raw]

    async def fetch_recent_activities(self) -> list[WoddleActivity]:
        """Fetch recent activities from the user profile (summary only)."""
        data = await self._request("GET", f"{WODDLE_API_V1}/user/profile")
        details = data.get("details", {}) if isinstance(data, dict) else {}
        raw = details.get("activities", [])
        return [WoddleActivity.from_api(a) for a in raw]

    # ── Charts ──────────────────────────────────────────────────────

    async def fetch_weight_chart(
        self,
        baby_id: str,
        start_date: str,
        end_date: str,
        time_span: str = "day",
        tz: str = "America/Los_Angeles",
    ) -> dict:
        """Fetch weight chart data for a date range."""
        return await self._request(
            "GET",
            f"{WODDLE_ACTIVITY_BASE}/charts/{baby_id}/weight"
            f"?timeSpan={time_span}&startDate={start_date}"
            f"&endDate={end_date}&timezone={tz}",
        )

    async def fetch_feeding_chart(
        self,
        baby_id: str,
        start_date: str,
        end_date: str,
        time_span: str = "day",
        tz: str = "America/Los_Angeles",
    ) -> dict:
        """Fetch feeding chart data for a date range."""
        return await self._request(
            "GET",
            f"{WODDLE_ACTIVITY_BASE}/charts/{baby_id}/feeding"
            f"?timeSpan={time_span}&startDate={start_date}"
            f"&endDate={end_date}&timezone={tz}",
        )

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
        await self.auth.close()
