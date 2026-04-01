"""Tests for pywoddle.models."""

from pywoddle.models import (
    WoddleActivity,
    WoddleBaby,
    WoddleDashboard,
    WoddleDashboardActivity,
    WoddleDevice,
    WoddleUserProfile,
)


# ── WoddleBaby ─────────────────────────────────────────────────

def test_baby_from_api():
    data = {
        "id": "baby-123",
        "first_name": "Winston",
        "last_name": "Smith",
        "dob": "2026-05-01",
        "due_date": "05-04-2026",
        "gender": "male",
        "pounds": 7,
        "ounces": 8,
    }
    baby = WoddleBaby.from_api(data)
    assert baby.baby_id == "baby-123"
    assert baby.first_name == "Winston"
    assert baby.pounds == 7
    assert baby.ounces == 8


def test_baby_from_api_empty():
    baby = WoddleBaby.from_api({})
    assert baby.baby_id == ""
    assert baby.first_name == ""


# ── WoddleActivity ─────────────────────────────────────────────

def test_activity_from_api_weight():
    data = {
        "id": "w1",
        "activity_type": "weight",
        "value": 6.4375,
        "type": None,
        "sub_type": None,
        "log_time": "2026-04-01T07:59:46.195Z",
        "unit": "lbs",
        "is_birth_weight": False,
        "title": "6lbs 7oz",
    }
    act = WoddleActivity.from_api(data)
    assert act.activity_id == "w1"
    assert act.activity_type == "weight"
    assert act.weight_lbs == 6.4375
    assert act.unit == "lbs"
    assert act.title == "6lbs 7oz"
    assert act.is_birth_weight is False


def test_activity_from_api_diaper():
    data = {
        "id": "d1",
        "activity_type": "diaper",
        "type": "poop",
        "sub_type": "medium",
        "log_time": "2026-04-01T04:58:56.000Z",
        "title": "Poop - Medium",
    }
    act = WoddleActivity.from_api(data)
    assert act.activity_type == "diaper"
    assert act.sub_type == "poop"
    assert act.weight_lbs is None


def test_activity_from_api_sleep():
    data = {
        "id": "s1",
        "activity_type": "sleep",
        "details": 3600,
        "sub_type": "manual",
        "log_time": "2026-04-01T07:00:00.000Z",
    }
    act = WoddleActivity.from_api(data)
    assert act.sleep_duration_seconds == 3600


def test_activity_sleep_duration_from_dict():
    data = {
        "id": "s2",
        "activity_type": "sleep",
        "details": {"sleep_duration": {"duration": 7200}},
        "log_time": "2026-04-01T07:00:00.000Z",
    }
    act = WoddleActivity.from_api(data)
    assert act.sleep_duration_seconds == 7200


def test_activity_from_api_feeding():
    data = {
        "id": "f1",
        "activity_type": "feeding",
        "type": "nursing",
        "details": 420,
        "log_time": "2026-04-01T08:00:00.000Z",
        "activityDetails": {
            "left_duration_total": 300,
            "right_duration_total": 120,
        },
    }
    act = WoddleActivity.from_api(data)
    assert act.activity_type == "feeding"
    assert act.feeding_duration_seconds == 420
    assert act.activity_details["left_duration_total"] == 300


def test_activity_feeding_duration_from_details():
    data = {
        "id": "f2",
        "activity_type": "feeding",
        "type": "nursing",
        "details": None,
        "log_time": "2026-04-01T08:00:00.000Z",
        "activityDetails": {
            "left_duration_total": 300,
            "right_duration_total": 120,
        },
    }
    act = WoddleActivity.from_api(data)
    assert act.feeding_duration_seconds == 420


def test_activity_from_api_summary():
    """Test activity from profile summary (minimal fields)."""
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
    assert act.value is None


def test_activity_from_api_empty():
    act = WoddleActivity.from_api({})
    assert act.activity_id == ""
    assert act.weight_lbs is None
    assert act.sleep_duration_seconds is None
    assert act.feeding_duration_seconds is None


# ── WoddleDashboard ────────────────────────────────────────────

def test_dashboard_from_api(dashboard_response):
    dashboard = WoddleDashboard.from_api(dashboard_response)
    assert dashboard.baby_id == "baby-1-id"
    assert len(dashboard.activities) == 3
    assert "weight" in dashboard.activity_type_ids
    assert "feeding" in dashboard.activity_type_ids
    assert "sleep" in dashboard.activity_type_ids
    assert dashboard.activity_type_ids["weight"] == "weight-type-uuid"


def test_dashboard_activity_latest():
    data = {
        "type_id": "t1",
        "type": "weight",
        "latestActivity": {
            "id": "w1",
            "value": 6.4375,
            "log_time": "2026-04-01T07:59:46.195Z",
            "activity_type": "weight",
        },
    }
    da = WoddleDashboardActivity.from_api(data)
    assert da.type_id == "t1"
    assert da.activity_type == "weight"
    assert da.latest_activity is not None
    assert da.latest_activity.value == 6.4375


def test_dashboard_activity_no_latest():
    data = {"type_id": "t1", "type": "diaper", "latestActivity": None}
    da = WoddleDashboardActivity.from_api(data)
    assert da.latest_activity is None


# ── WoddleDevice ───────────────────────────────────────────────

def test_device_from_api():
    data = {
        "deviceID": "SERIAL-123",
        "name": "My Pad",
        "fw_version": "1.2.187",
        "possession": True,
    }
    device = WoddleDevice.from_api(data)
    assert device.device_id == "SERIAL-123"
    assert device.firmware_version == "1.2.187"


def test_device_defaults():
    device = WoddleDevice.from_api({})
    assert device.name == "Woddle Changing Pad"


# ── WoddleUserProfile ──────────────────────────────────────────

def test_user_profile_from_api():
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
    assert profile.measurement == "Metric"
