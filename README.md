# pywoddle

Async Python client for the [Woddle Smart Baby Scale](https://www.woddlebaby.com/) API.

## Installation

```bash
pip install pywoddle
```

## Usage

```python
import asyncio
from pywoddle import WoddleAuth, WoddleClient

async def main():
    auth = WoddleAuth(email="you@example.com", password="yourpassword")
    await auth.authenticate()

    client = WoddleClient(auth)

    # List babies on your account
    babies = await client.fetch_babies()
    for baby in babies:
        print(f"{baby.first_name} (due: {baby.due_date})")

    # Get recent activities (diapers, feedings, etc.)
    activities = await client.fetch_recent_activities()
    for activity in activities:
        print(f"{activity.baby_name}: {activity.activity_type}/{activity.sub_type} at {activity.log_time}")

    # List registered devices
    devices = await client.fetch_devices()
    for device in devices:
        print(f"{device.name} (serial: {device.device_id}, fw: {device.firmware_version})")

    await client.close()

asyncio.run(main())
```

## API Reference

### Authentication

- `WoddleAuth(email, password, session=None)` — Create auth instance
- `await auth.authenticate()` — Login and obtain JWT token
- `await auth.ensure_valid_token()` — Re-authenticate if token expired
- `await auth.close()` — Close the HTTP session

### Client

- `WoddleClient(auth)` — Create API client
- `await client.fetch_babies()` — List all babies → `list[WoddleBaby]`
- `await client.fetch_baby_details(baby_id)` — Get baby details → `WoddleBaby`
- `await client.fetch_recent_activities()` — Recent activities → `list[WoddleActivity]`
- `await client.fetch_devices()` — Registered devices → `list[WoddleDevice]`
- `await client.fetch_user_profile()` — User profile → `WoddleUserProfile`
- `await client.close()` — Close the HTTP session

### Models

- `WoddleBaby` — `baby_id`, `first_name`, `last_name`, `due_date`, `date_of_birth`, `gender`
- `WoddleActivity` — `activity_id`, `baby_name`, `activity_type`, `sub_type`, `log_time`
- `WoddleDevice` — `device_id`, `name`, `firmware_version`, `possession`
- `WoddleUserProfile` — `user_id`, `first_name`, `last_name`, `email`, `relationship`, `measurement`

### Exceptions

- `WoddleError` — Base exception
- `WoddleAuthError` — Authentication failures
- `WoddleApiError` — API request errors (includes `status_code` attribute)

## License

MIT
