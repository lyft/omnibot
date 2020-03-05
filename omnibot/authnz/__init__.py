"""
Authentication and authorization module for omnibot. This module applies
checks defined in the ``authorization`` section of the configuration. See
the documentation on checks:

* :func:`omnibot.authnz:enforce_checks`

Also see the documentation for the built-in checks:

* :func:`omnibot.authnz.envoy_checks:envoy_internal_check`
* :func:`omnibot.authnz.envoy_checks:envoy_permissions_check`
"""
import importlib
import logging
import re
from functools import wraps

from flask import (
    abort,
    request
)

from omnibot import settings

logger = logging.getLogger(__name__)


def enforce_checks(f):
    """
    Enforce a list of checks, defined in the ``authorization`` configuration.

    For example, the following configuration would enforce two checks, one of
    which passes a kwarg into a check::

        authorization:
          checks:
            - module: "omnibot.authnz.envoy_checks:envoy_internal_check"
              kwargs:
                header: 'x-nginx-internal'
            - module: "omnibot.authnz.envoy_checks:envoy_permissions_check"

    Checks will be executed in the order defined by the list. All checks must
    pass for a request to be accepted.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        checks = settings.AUTHORIZATION.get('checks', [])
        if not checks:
            logger.warning(
                'No checks set in the authorization section of the configuration;'
                ' denying access to API calls for sanity sake'
            )
            return abort(403)
        for check in checks:
            module_name, function_name = check['module'].split(':')
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            func_kwargs = check.get('kwargs', {})
            response = function(**func_kwargs)
            if response is not True:
                return abort(403)
        return f(*args, **kwargs)
    return decorated


def allowed_paths(paths):
    """
    Perform a check against the paths configured for this function, to ensure
    we only allow basic access to the paths if they're explicitly defined. For
    example::

        authorization:
          checks:
            - module: "omnibot.authnz:allowed_paths"
              kwargs:
                paths:
                  - "/api/v1/slack/event"
                  - "/api/v1/slack/slash_command"
                  - "/api/v1/slack/interactive"
                  - "/api/v1/slack/get_team/.*"
    """
    for path in paths:
        pattern = re.compile(path)
        if pattern.match(request.path):
            return True
    return False
