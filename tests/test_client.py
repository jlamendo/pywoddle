"""Tests for pywoddle.client."""

import pytest
from aioresponses import aioresponses

from pywoddle import WoddleAuth, WoddleClient
from pywoddle.const import WODDLE_ACTIVITY_BASE, WODDLE_API_V1
from pywoddle.exceptions import WoddleApiError


@pytest.mark.asyncio
async def test_fetch_babies(login_response, babies_response):
    """Test fetching babies."""
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
        assert babies[0].due_date == "06-01-2026"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_babies_empty(login_response):
    """Test fetching babies when none exist."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(
            f"{WODDLE_API_V1}/baby/fetchBabies",
            payload={"status": 200, "babies": []},
        )

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        babies = await client.fetch_babies()
        assert babies == []

        await client.close()


@pytest.mark.asyncio
async def test_fetch_recent_activities(login_response, profile_response):
    """Test fetching recent activities."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/user/profile", payload=profile_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        activities = await client.fetch_recent_activities()
        assert len(activities) == 2
        assert activities[0].activity_id == "act-1"
        assert activities[0].activity_type == "diaper"
        assert activities[0].sub_type == "poop"
        assert activities[0].baby_name == "TestBaby"
        assert activities[1].activity_type == "feeding"
        assert activities[1].sub_type == "breast"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_devices(login_response, devices_response):
    """Test fetching devices."""
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
        assert devices[0].name == "Woddle Changing Pad"
        assert devices[0].possession is True

        await client.close()


@pytest.mark.asyncio
async def test_fetch_user_profile(login_response, user_details_response):
    """Test fetching user profile."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/user/details", payload=user_details_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        profile = await client.fetch_user_profile()
        assert profile.user_id == "test-user-id"
        assert profile.first_name == "Test"
        assert profile.last_name == "User"
        assert profile.measurement == "Imperial"

        await client.close()


@pytest.mark.asyncio
async def test_fetch_baby_details(login_response):
    """Test fetching a specific baby's details."""
    baby_response = {
        "status": 200,
        "data": {
            "id": "baby-1-id",
            "first_name": "TestBaby",
            "last_name": "Smith",
            "due_date": "06-01-2026",
            "dob": "",
            "gender": "male",
        },
    }
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        mock.get(f"{WODDLE_API_V1}/baby/get/baby-1-id", payload=baby_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        baby = await client.fetch_baby_details("baby-1-id")
        assert baby.baby_id == "baby-1-id"
        assert baby.first_name == "TestBaby"
        assert baby.gender == "male"

        await client.close()


@pytest.mark.asyncio
async def test_request_401_retry(login_response, babies_response):
    """Test that 401 triggers re-auth and retry."""
    with aioresponses() as mock:
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        # First request returns 401
        mock.get(f"{WODDLE_API_V1}/baby/fetchBabies", status=401)
        # Re-auth
        mock.post(f"{WODDLE_API_V1}/login", payload=login_response)
        # Retry succeeds
        mock.get(f"{WODDLE_API_V1}/baby/fetchBabies", payload=babies_response)

        auth = WoddleAuth(email="test@example.com", password="testpass")
        await auth.authenticate()
        client = WoddleClient(auth)

        babies = await client.fetch_babies()
        assert len(babies) == 1

        await client.close()


@pytest.mark.asyncio
async def test_request_500_raises(login_response):
    """Test that server errors raise WoddleApiError."""
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
