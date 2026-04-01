"""Tests for pywoddle.exceptions."""

from pywoddle.exceptions import WoddleApiError, WoddleAuthError, WoddleError


def test_exception_hierarchy():
    """Test that all exceptions inherit from WoddleError."""
    assert issubclass(WoddleAuthError, WoddleError)
    assert issubclass(WoddleApiError, WoddleError)


def test_api_error_status_code():
    """Test WoddleApiError stores status code."""
    err = WoddleApiError("Not found", status_code=404)
    assert str(err) == "Not found"
    assert err.status_code == 404


def test_api_error_no_status_code():
    """Test WoddleApiError without status code."""
    err = WoddleApiError("Connection failed")
    assert err.status_code is None


def test_auth_error():
    """Test WoddleAuthError."""
    err = WoddleAuthError("Invalid credentials")
    assert str(err) == "Invalid credentials"
    assert isinstance(err, WoddleError)
