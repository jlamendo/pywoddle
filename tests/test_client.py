"""Tests for pywoddle.client."""

import pytest
from aioresponses import aioresponses

from pywoddle import WoddleAuth, WoddleClient
from pywoddle.const import WODDLE_ACTIVITY_BASE, WODDLE_API_V1
from pywoddle.exceptions import WoddleApiError


@pytest.mark.asyncio
async def test_fetch_babies(login_response, babies_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/baby/fetchBabies", payload=babies_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        babies = await client.fetch_babies()
        assert len(babies) == 1
        assert babies[0].first_name == "TestBaby"
        assert babies[0].baby_id == "baby-1-id"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_recent_activities(login_response, profile_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/user/profile", payload=profile_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        activities = await client.fetch_recent_activities()
        assert len(activities) == 2
        assert activities[0].activity_type == "diaper"
        assert activities[0].sub_type == "poop"
        assert activities[1].activity_type == "feeding"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_dashboard(login_response, dashboard_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(
            f"{WODDLE_ACTIVITY_BASE}/dashboard/baby-1-id",
            payload=dashboard_response,
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        dashboard = await client.fetch_dashboard("baby-1-id")
        assert dashboard.baby_id == "baby-1-id"
        assert len(dashboard.activities) == 3
        assert "weight" in dashboard.activity_type_ids
        assert dashboard.activity_type_ids["weight"] == "weight-type-uuid"

        # Check latest weight activity
        weight_entry = next(
            a for a in dashboard.activities if a.activity_type == "weight"
        )
        assert weight_entry.latest_activity is not None
        assert weight_entry.latest_activity.value == 6.4375

        await client.close()


@pytest.mark.asyncio
async def test_fetch_calendar(login_response, calendar_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(
            f"{WODDLE_ACTIVITY_BASE}/dashboard/baby-1-id/calendar?date=2026-04-01&timezone=America/Los_Angeles",
            payload=calendar_response,
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        activities = await client.fetch_calendar(
            "baby-1-id", date="2026-04-01", tz="America/Los_Angeles"
        )
        assert len(activities) == 4

        weight = next(a for a in activities if a.activity_type == "weight")
        assert weight.value == 6.4375
        assert weight.unit == "lbs"
        assert weight.title == "6lbs 7oz"
        assert weight.is_birth_weight is False

        diaper = next(a for a in activities if a.activity_type == "diaper")
        assert diaper.sub_type == "poop"

        sleep = next(a for a in activities if a.activity_type == "sleep")
        assert sleep.sleep_duration_seconds == 3600

        feeding = next(a for a in activities if a.activity_type == "feeding")
        assert feeding.feeding_duration_seconds == 420

        await client.close()


@pytest.mark.asyncio
async def test_fetch_history(login_response, history_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(
            f"{WODDLE_ACTIVITY_BASE}/fetchHistory/baby-1-id/weight-type-uuid",
            payload=history_response,
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        activities = await client.fetch_history("baby-1-id", "weight-type-uuid")
        assert len(activities) == 1
        assert activities[0].activity_type == "weight"
        assert activities[0].weight_lbs == 6.4375
        assert activities[0].unit == "lbs"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_devices(login_response, devices_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(
            f"{WODDLE_ACTIVITY_BASE}/device/fetchDevices",
            payload=devices_response,
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        devices = await client.fetch_devices()
        assert len(devices) == 1
        assert devices[0].device_id == "TEST-SERIAL-123"
        assert devices[0].firmware_version == "1.2.187"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_user_profile(login_response, user_details_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/user/details", payload=user_details_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        profile = await client.fetch_user_profile()
        assert profile.user_id == "test-user-id"
        assert profile.first_name == "Test"
        assert profile.measurement == "Imperial"

        await client.close()


@pytest.mark.asyncio
async def test_request_401_retry(login_response, babies_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/baby/fetchBabies", status=401)
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/baby/fetchBabies", payload=babies_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        babies = await client.fetch_babies()
        assert len(babies) == 1

        await client.close()


@pytest.mark.asyncio
async def test_request_500_raises(login_response):
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(
            f"{WODDLE_API_V1}/baby/fetchBabies",
            status=500,
            body="Internal Server Error",
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        with pytest.raises(WoddleApiError, match="API error 500"):
            await client.fetch_babies()

        await client.close()
