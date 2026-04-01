"""Tests for pywoddle.models."""

from pywoddle.models import (
    WoddleActivity,
    WoddleBaby,
    WoddleDevice,
    WoddleUserProfile,
)


def test_baby_from_api():
    """Test WoddleBaby.from_api with full data."""
    data = {
        "id": "baby-123",
        "first_name": "Winston",
        "last_name": "Smith",
        "dob": "2026-05-01",
        "due_date": "05-04-2026",
        "gender": "male",
        "photo": "https://example.com/photo.jpg",
        "pounds": 7,
        "ounces": 8,
    }
    baby = WoddleBaby.from_api(data)
    assert baby.baby_id == "baby-123"
    assert baby.first_name == "Winston"
    assert baby.last_name == "Smith"
    assert baby.due_date == "05-04-2026"
    assert baby.gender == "male"
    assert baby.pounds == 7
    assert baby.ounces == 8


def test_baby_from_api_minimal():
    """Test WoddleBaby.from_api with minimal data."""
    baby = WoddleBaby.from_api({"id": "b1", "first_name": "Test"})
    assert baby.baby_id == "b1"
    assert baby.first_name == "Test"
    assert baby.last_name == ""
    assert baby.photo is None


def test_baby_from_api_empty():
    """Test WoddleBaby.from_api with empty dict."""
    baby = WoddleBaby.from_api({})
    assert baby.baby_id == ""
    assert baby.first_name == ""


def test_activity_from_api():
    """Test WoddleActivity.from_api."""
    data = {
        "activity_id": "act-1",
        "first_name": "Winston",
        "type": "poop",
        "activity_type": "diaper",
        "log_time": "2026-04-01T04:58:56.000Z",
    }
    act = WoddleActivity.from_api(data)
    assert act.activity_id == "act-1"
    assert act.baby_name == "Winston"
    assert act.activity_type == "diaper"
    assert act.sub_type == "poop"
    assert act.log_time == "2026-04-01T04:58:56.000Z"


def test_activity_from_api_empty():
    """Test WoddleActivity.from_api with empty dict."""
    act = WoddleActivity.from_api({})
    assert act.activity_id == ""
    assert act.activity_type == ""


def test_device_from_api():
    """Test WoddleDevice.from_api."""
    data = {
        "deviceID": "SERIAL-123",
        "name": "My Woddle Pad",
        "fw_version": "1.2.187",
        "possession": True,
    }
    device = WoddleDevice.from_api(data)
    assert device.device_id == "SERIAL-123"
    assert device.name == "My Woddle Pad"
    assert device.firmware_version == "1.2.187"
    assert device.possession is True


def test_device_from_api_defaults():
    """Test WoddleDevice defaults."""
    device = WoddleDevice.from_api({})
    assert device.name == "Woddle Changing Pad"
    assert device.possession is True


def test_user_profile_from_api():
    """Test WoddleUserProfile.from_api."""
    data = {
        "id": "user-1",
        "first_name": "Jon",
        "last_name": "Doe",
        "email": "jon@example.com",
        "relationship": "Father",
        "measurement": "Metric",
    }
    profile = WoddleUserProfile.from_api(data)
    assert profile.user_id == "user-1"
    assert profile.first_name == "Jon"
    assert profile.measurement == "Metric"
    assert profile.relationship == "Father"
