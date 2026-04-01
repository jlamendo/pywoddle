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
    """Mock fetchBabies response."""
    return {
        "status": 200,
        "message": "Your account details have been retrieved.",
        "babies": [
            {
                "id": "baby-1-id",
                "first_name": "TestBaby",
                "last_name": "Smith",
                "dob": "",
                "due_date": "06-01-2026",
                "gender": "",
                "pounds": None,
                "ounces": None,
                "inches": None,
                "length_inches": None,
                "document_id": None,
                "status": None,
                "photo": None,
            }
        ],
    }


@pytest.fixture
def profile_response():
    """Mock user/profile response with activities."""
    return {
        "status": 200,
        "message": "Your account details have been retrieved.",
        "details": {
            "user": {
                "id": "test-user-id",
                "first_name": "Test",
                "last_name": "User",
                "dob": "01-01-1990",
                "relationship": "Father",
                "document_id": None,
                "registration_debug_mode": False,
                "vitals_settings": {},
            },
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
                    "type": "breast",
                    "activity_type": "feeding",
                    "log_time": "2026-04-01T06:30:00.000Z",
                },
            ],
        },
    }


@pytest.fixture
def devices_response():
    """Mock device/fetchDevices response."""
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
    """Mock user/details response."""
    return {
        "status": 200,
        "message": "Your account details have been retrieved.",
        "details": {
            "id": "test-user-id",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "dob": "01-01-1990",
            "relationship": "Father",
            "measurement": "Imperial",
            "babies": [],
        },
    }
