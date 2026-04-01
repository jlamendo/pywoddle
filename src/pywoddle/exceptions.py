"""Exceptions for the pywoddle library."""


class WoddleError(Exception):
    """Base exception for pywoddle."""


class WoddleAuthError(WoddleError):
    """Authentication error."""


class WoddleApiError(WoddleError):
    """API request error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
