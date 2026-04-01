"""Data models for the pywoddle library."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
    """Represents a tracked activity (diaper, feeding, sleep, weight, pumping, etc.).

    The full activity record from calendar/fetchHistory includes value, unit,
    details, and sub_type. The summary from user/profile only has activity_type,
    type, and log_time.
    """

    activity_id: str
    baby_name: str
    activity_type: str  # "diaper", "feeding", "sleep", "weight", "pumping"
    sub_type: str  # "poop", "nursing", "manual", "separate", etc.
    log_time: str  # ISO 8601 timestamp
    value: float | None = None  # Weight in lbs, sleep duration, etc.
    unit: str | None = None  # "lbs", etc.
    details: Any = None  # Feeding details, sleep duration, etc.
    note: str | None = None
    is_birth_weight: bool = False
    is_edited: bool = False
    title: str | None = None  # Human-readable title (e.g. "6lbs 7oz")
    activity_details: dict | None = None  # Nested details (nursing sides, etc.)
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict) -> WoddleActivity:
        return cls(
            activity_id=data.get("id") or data.get("activity_id", ""),
            baby_name=data.get("first_name", ""),
            activity_type=data.get("activity_type", ""),
            sub_type=data.get("type") or data.get("sub_type") or "",
            log_time=data.get("log_time", ""),
            value=data.get("value"),
            unit=data.get("unit"),
            details=data.get("details"),
            note=data.get("note"),
            is_birth_weight=data.get("is_birth_weight", False),
            is_edited=data.get("is_edited", False),
            title=data.get("title"),
            activity_details=data.get("activityDetails"),
            raw=data,
        )

    @property
    def weight_lbs(self) -> float | None:
        """Weight value in pounds (for weight activities)."""
        if self.activity_type == "weight" and self.value is not None:
            return self.value
        return None

    @property
    def sleep_duration_seconds(self) -> int | None:
        """Sleep duration in seconds (for sleep activities)."""
        if self.activity_type == "sleep" and self.details is not None:
            if isinstance(self.details, (int, float)):
                return int(self.details)
            if isinstance(self.details, dict):
                sd = self.details.get("sleep_duration", {})
                return sd.get("duration") if isinstance(sd, dict) else None
        return None

    @property
    def feeding_duration_seconds(self) -> int | None:
        """Total feeding duration in seconds."""
        if self.activity_type == "feeding" and self.details is not None:
            if isinstance(self.details, (int, float)):
                return int(self.details)
        if self.activity_details:
            left = self.activity_details.get("left_duration_total", 0) or 0
            right = self.activity_details.get("right_duration_total", 0) or 0
            total = left + right
            return total if total > 0 else None
        return None


@dataclass
class WoddleDashboardActivity:
    """An activity type entry from the dashboard."""

    type_id: str  # Activity type UUID (used for fetchHistory)
    activity_type: str  # "feeding", "sleep", "weight", "diaper", "pumping"
    latest_activity: WoddleActivity | None = None

    @classmethod
    def from_api(cls, data: dict) -> WoddleDashboardActivity:
        latest_raw = data.get("latestActivity")
        latest = WoddleActivity.from_api(latest_raw) if latest_raw else None
        return cls(
            type_id=data.get("type_id", ""),
            activity_type=data.get("type", ""),
            latest_activity=latest,
        )


@dataclass
class WoddleDashboard:
    """Dashboard data for a baby, including activity type IDs."""

    baby_id: str = ""
    activities: list[WoddleDashboardActivity] = field(default_factory=list)
    activity_type_ids: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict) -> WoddleDashboard:
        raw_data = data.get("data", {}) if isinstance(data, dict) else {}
        baby_details = raw_data.get("babyDetails", {})
        raw_activities = raw_data.get("activities", [])

        activities = [WoddleDashboardActivity.from_api(a) for a in raw_activities]
        type_ids = {a.activity_type: a.type_id for a in activities}

        return cls(
            baby_id=baby_details.get("id", ""),
            activities=activities,
            activity_type_ids=type_ids,
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
        return cls(
            user_id=data.get("id", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            relationship=data.get("relationship", ""),
            measurement=data.get("measurement", "Imperial"),
        )
