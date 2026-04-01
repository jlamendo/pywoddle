"""Data models for the pywoddle library."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WoddleBaby:
    """Represents a baby tracked by Woddle."""

    baby_id: str
    first_name: str
    last_name: str = ""
    due_date: str = ""
    date_of_birth: str = ""
    gender: str = ""
    photo: str | None = None
    pounds: float | None = None
    ounces: float | None = None

    @classmethod
    def from_api(cls, data: dict) -> WoddleBaby:
        """Create from API response dict."""
        return cls(
            baby_id=data.get("id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            due_date=data.get("due_date", ""),
            date_of_birth=data.get("dob", ""),
            gender=data.get("gender", ""),
            photo=data.get("photo"),
            pounds=data.get("pounds"),
            ounces=data.get("ounces"),
        )


@dataclass
class WoddleActivity:
    """Represents a tracked activity (diaper, feeding, sleep, weight, etc.)."""

    activity_id: str
    baby_name: str
    activity_type: str  # "diaper", "feeding", "sleep", "weight", etc.
    sub_type: str  # "poop", "pee", "breast", "bottle", etc.
    log_time: str  # ISO 8601 timestamp

    @classmethod
    def from_api(cls, data: dict) -> WoddleActivity:
        """Create from API response dict."""
        return cls(
            activity_id=data.get("activity_id", ""),
            baby_name=data.get("first_name", ""),
            activity_type=data.get("activity_type", ""),
            sub_type=data.get("type", ""),
            log_time=data.get("log_time", ""),
        )


@dataclass
class WoddleDevice:
    """Represents a Woddle changing pad device."""

    device_id: str
    name: str
    firmware_version: str
    possession: bool = True

    @classmethod
    def from_api(cls, data: dict) -> WoddleDevice:
        """Create from API response dict."""
        return cls(
            device_id=data.get("deviceID", ""),
            name=data.get("name", "Woddle Changing Pad"),
            firmware_version=data.get("fw_version", ""),
            possession=data.get("possession", True),
        )


@dataclass
class WoddleUserProfile:
    """User profile information."""

    user_id: str
    first_name: str
    last_name: str
    email: str = ""
    relationship: str = ""
    measurement: str = "Imperial"

    @classmethod
    def from_api(cls, data: dict) -> WoddleUserProfile:
        """Create from API response dict."""
        return cls(
            user_id=data.get("id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            relationship=data.get("relationship", ""),
            measurement=data.get("measurement", "Imperial"),
        )
