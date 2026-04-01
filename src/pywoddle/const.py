"""Constants for the pywoddle library."""

WODDLE_API_BASE = "https://app.woddlebaby.com"
WODDLE_ACTIVITY_BASE = f"{WODDLE_API_BASE}/activity/v1"
WODDLE_API_V1 = f"{WODDLE_API_BASE}/api/v1"

# Token refresh interval (hours) — JWT has ~30 day expiry but refresh proactively
TOKEN_REFRESH_HOURS = 12
