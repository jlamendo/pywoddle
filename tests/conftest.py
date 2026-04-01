"""Test fixtures for pywoddle."""

import pytest


@pytest.fixture
def login_response():
    """Mock successful login response."""
    return {
        "status": 200,
        "message": "Welcome back! You've successfully logged in.",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InRlc3QtdXNlci1pZCJ9.fake",
        "refreshToken": "fake-refresh-token",
    }


@pytest.fixture
def babies_response():
    return {
        "status": 200,
        "babies": [
            {
                "id": "baby-1-id",
                "first_name": "TestBaby",
                "last_name": "Smith",
                "dob": "",
                "due_date": "06-01-2026",
                "gender": "boy",
            }
        ],
    }


@pytest.fixture
def profile_response():
    return {
        "status": 200,
        "details": {
            "user": {"id": "test-user-id", "first_name": "Test", "last_name": "User"},
            "activities": [
                {
                    "activity_id": "act-1",
                    "first_name": "TestBaby",
                    "type": "poop",
                    "activity_type": "diaper",
                    "log_time": "2026-04-01T04:58:56.000Z",
                },
                {
                    "activity_id": "act-2",
                    "first_name": "TestBaby",
                    "type": "nursing",
                    "activity_type": "feeding",
                    "log_time": "2026-04-01T06:30:00.000Z",
                },
            ],
        },
    }


@pytest.fixture
def dashboard_response():
    return {
        "status": 200,
        "data": {
            "babyDetails": {"id": "baby-1-id", "dob": "", "gender": "boy"},
            "activities": [
                {
                    "type_id": "weight-type-uuid",
                    "type": "weight",
                    "latestActivity": {
                        "id": "w1",
                        "activity_type_id": "weight-type-uuid",
                        "value": 6.4375,
                        "log_time": "2026-04-01T07:59:46.195Z",
                        "type": None,
                        "sub_type": None,
                        "is_birth_weight": False,
                        "activity_type": "weight",
                    },
                },
                {
                    "type_id": "feeding-type-uuid",
                    "type": "feeding",
                    "latestActivity": {
                        "id": "f1",
                        "activity_type_id": "feeding-type-uuid",
                        "value": None,
                        "log_time": "2026-04-01T08:00:00.000Z",
                        "type": "nursing",
                        "sub_type": "manual",
                        "details": 420,
                        "activity_type": "feeding",
                        "activityDetails": {
                            "left_duration_total": 300,
                            "right_duration_total": 120,
                        },
                    },
                },
                {
                    "type_id": "sleep-type-uuid",
                    "type": "sleep",
                    "latestActivity": {
                        "id": "s1",
                        "activity_type_id": "sleep-type-uuid",
                        "value": None,
                        "log_time": "2026-04-01T07:00:00.000Z",
                        "type": None,
                        "sub_type": "manual",
                        "details": 3600,
                        "activity_type": "sleep",
                    },
                },
            ],
        },
    }


@pytest.fixture
def calendar_response():
    return {
        "status": 200,
        "activities": [
            {
                "id": "act-diaper",
                "activity_type": "diaper",
                "value": None,
                "type": "poop",
                "sub_type": "medium",
                "log_time": "2026-04-01T04:58:56.000Z",
                "title": "Poop - Medium",
            },
            {
                "id": "act-weight",
                "activity_type": "weight",
                "value": 6.4375,
                "type": None,
                "sub_type": None,
                "log_time": "2026-04-01T07:59:46.195Z",
                "unit": "lbs",
                "is_birth_weight": False,
                "title": "6lbs 7oz",
            },
            {
                "id": "act-sleep",
                "activity_type": "sleep",
                "value": None,
                "type": None,
                "sub_type": "manual",
                "details": 3600,
                "log_time": "2026-04-01T07:00:00.000Z",
                "title": "1h",
            },
            {
                "id": "act-feeding",
                "activity_type": "feeding",
                "value": None,
                "type": "nursing",
                "sub_type": "manual",
                "details": 420,
                "log_time": "2026-04-01T08:00:00.000Z",
                "activityDetails": {
                    "left_duration_total": 300,
                    "right_duration_total": 120,
                },
            },
        ],
    }


@pytest.fixture
def history_response():
    return {
        "status": 200,
        "activities": [
            {
                "id": "w1",
                "activity_type": "weight",
                "value": 6.4375,
                "type": None,
                "sub_type": None,
                "log_time": "2026-04-01T07:59:46.195Z",
                "unit": "lbs",
                "is_birth_weight": False,
            }
        ],
    }


@pytest.fixture
def devices_response():
    return {
        "status": 200,
        "data": [
            {
                "deviceID": "TEST-SERIAL-123",
                "possession": True,
                "name": "Woddle Changing Pad",
                "fw_version": "1.2.187",
            }
        ],
    }


@pytest.fixture
def user_details_response():
    return {
        "status": 200,
        "details": {
            "id": "test-user-id",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "relationship": "Father",
            "measurement": "Imperial",
        },
    }
