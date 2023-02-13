from omnibot.app import app
from omnibot.authnz import envoy_checks


def test_envoy_internal_check(mocker):
    # Test an internal route with the header set
    with app.test_request_context(
        path="/api/v1/slack/get_team/testteam",
        method="GET",
        headers={"x-envoy-internal": "true"},
    ):
        result = envoy_checks.envoy_internal_check()
        assert result is True

    # Test an internal route with the header set to False
    with app.test_request_context(
        path="/api/v1/slack/get_team/testteam",
        method="GET",
        headers={"x-envoy-internal": "false"},
    ):
        result = envoy_checks.envoy_internal_check()
        assert result is False

    # Test an internal route with the header not set
    with app.test_request_context(path="/api/v1/slack/get_team/testteam", method="GET"):
        result = envoy_checks.envoy_internal_check()
        assert result is False

    # Test a route that isn't set as internal only
    with app.test_request_context(path="/api/v1/slack/event", method="POST"):
        result = envoy_checks.envoy_internal_check()
        assert result is True


def test_envoy_permissions_check(mocker):
    with app.test_request_context(
        path="/api/v1/slack/event",
        method="POST",
        headers={"x-envoy-downstream-service-cluster": "envoy"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is True

    with app.test_request_context(
        path="/api/v1/slack/event",
        method="POST",
        headers={"x-envoy-downstream-service-cluster": "notasubject"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is False

    with app.test_request_context(path="/api/v1/slack/event", method="POST"):
        result = envoy_checks.envoy_permissions_check()
        assert result is False

    with app.test_request_context(
        path="/api/v1/slack/get_user/testteam/echobot/test@example.com",
        method="GET",
        headers={"x-envoy-downstream-service-cluster": "someservice"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is True

    with app.test_request_context(
        path="/api/v1/slack/get_user/testteam/unauthbot/test@example.com",
        method="GET",
        headers={"x-envoy-downstream-service-cluster": "someservice"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is False

    with app.test_request_context(
        path="/api/v1/slack/get_user/testteam/echobot/test@example.com",
        method="GET",
        headers={"x-envoy-downstream-service-cluster": "unauthservice"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is False

    with app.test_request_context(
        path="/api/v2/slack/action/test2ndteam/pingbot",
        method="POST",
        headers={"x-envoy-downstream-service-cluster": "service-test"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is True

    with app.test_request_context(
        path="/api/v2/slack/action/test2ndteam/pingbot",
        method="POST",
        headers={"x-envoy-downstream-service-cluster": "service"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is True

    with app.test_request_context(
        path="/api/v2/slack/action/test2ndteam/pingbot",
        method="POST",
        headers={"x-envoy-downstream-service-cluster": "unauthservice"},
    ):
        result = envoy_checks.envoy_permissions_check()
        assert result is False
