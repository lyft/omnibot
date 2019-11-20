import pytest
from werkzeug.exceptions import HTTPException

from omnibot.app import app
from omnibot import authnz


def test_enforce_checks(mocker):
    @authnz.enforce_checks
    def some_test_function():
        return True

    allowed_paths_check = mocker.patch(
        'omnibot.authnz.allowed_paths'
    )
    allowed_paths_check.return_value = True
    envoy_internal_check = mocker.patch(
        'omnibot.authnz.envoy_checks.envoy_internal_check'
    )
    envoy_internal_check.return_value = True
    envoy_permissions_check = mocker.patch(
        'omnibot.authnz.envoy_checks.envoy_permissions_check'
    )
    envoy_permissions_check.return_value = True

    assert some_test_function() is True

    envoy_internal_check.return_value = False

    with pytest.raises(HTTPException) as http_error:
        some_test_function()
        assert http_error.exception.code == 403

    envoy_internal_check.return_value = True
    envoy_permissions_check.return_value = False

    with pytest.raises(HTTPException) as http_error:
        some_test_function()
        assert http_error.exception.code == 403

    allowed_paths_check.return_value = False
    envoy_internal_check.return_value = False
    envoy_permissions_check.return_value = False

    with pytest.raises(HTTPException) as http_error:
        some_test_function()
        assert http_error.exception.code == 403


def test_allowed_paths(mocker):
    paths = [
        '/api/v1/slack/event',
        '/api/v1/slack/get_team/testteam',
        '/api/v2/slack/action/ateam/abot'
    ]
    # Test a basic post route
    with app.test_request_context(
            path='/api/v1/slack/event',
            method='POST'):
        result = authnz.allowed_paths(paths)
        assert result is True

    # Test a route that uses regex
    with app.test_request_context(
            path='/api/v1/slack/get_team/testteam',
            method='GET'):
        result = authnz.allowed_paths(paths)
        assert result is True

    # Test a route that's not allowed
    with app.test_request_context(
            path='/api/v2/slack/action/notateam/notabot',
            method='GET'):
        result = authnz.allowed_paths(paths)
        assert result is False
