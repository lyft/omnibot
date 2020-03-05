import logging
import re

from flask import request

from omnibot import settings

logger = logging.getLogger(__name__)


def _match_path(path_to_match, paths):
    for path in paths:
        pattern = re.compile(path)
        if pattern.match(path_to_match):
            return True
    return False


def _match_subject(subject_to_match, subject):
    pattern = re.compile(subject)
    if pattern.match(subject_to_match):
        return True
    return False


def envoy_internal_check(header='x-envoy-internal'):
    """
    Perform a check to ensure that the ``x-envoy-internal`` is set to 'true'.
    By default this check will apply to all routes, if enabled. It's possible
    to disable this check on a per-route basis in the permissions section of
    the authorization config, by setting ``internal_only: false`` in the
    relevant permissions section::

        authorization:
          permissions:
            slack_api:
              methods:
                - "POST"
              paths:
                - "/api/v1/slack/event"
                - "/api/v1/slack/slash_command"
                - "/api/v1/slack/interactive"
              # Do not require x-envoy-internal check for this set of paths
              internal_only: false
    """
    # Flask provides all headers as strings. The only acceptable string here
    # is 'true'
    envoy_internal = request.headers.get(header) == 'true'
    # Easy case. The header says the request is internal.
    if envoy_internal:
        return True
    # If the request isn't internal, let's see if we have a permission that
    # matches, which has internal_only set to False
    permissions = settings.AUTHORIZATION.get('permissions', {})
    for policy_name, policy in permissions.items():
        method_match = request.method in policy['methods']
        path_match = _match_path(request.path, policy['paths'])
        internal_only = policy.get('internal_only', True)
        if (method_match and path_match) and not internal_only:
            return True
    msg = ('Received an external request to internal endpoint={} method={}'
           ' header_value={}')
    logger.warning(msg.format(request.path, request.method, envoy_internal))
    return False


def _check_permission(permission):
    permissions = settings.AUTHORIZATION.get('permissions', {})
    policy = permissions.get(permission, {})
    # TODO: envoy RBAC spec allows for matching methods and paths as
    # individual checks. So for instance, a permission may allow for all GETs
    # without a particular path, or may allow all methods on particular paths.
    method_match = request.method in policy.get('methods', [])
    path_match = _match_path(request.path, policy.get('paths', []))
    if method_match and path_match:
        return True
    return False


def envoy_permissions_check(header='x-envoy-downstream-service-cluster'):
    """
    Perform a check against the defined permissions and bindings in the
    authorization configuration to ensure the service defined in the
    ``x-envoy-downstream-service-cluster`` header is allowed to access the path
    and method in the current request context. By default, if this check is
    enabled, all routes will be denied access unless a service defined in the
    bindings has permissions with a matching method and path.

    For example, the following configuration allows ``POST`` calls, from a
    service named ``envoy``, to a set of endpoints used to accept events from
    slack. It also allows a service that starts with the name ``echobot`` to
    post to into the ``testteam`` workspace, as the ``echobot`` slack app::

        authorization:
          permissions:
            slack_api:
              methods:
                - "POST"
              paths:
                - "/api/v1/slack/event"
                - "/api/v1/slack/slash_command"
                - "/api/v1/slack/interactive"
              # Do not require x-envoy-internal check for this set of paths
              # see (envoy_internal_check)
              internal_only: false
            echobot_slack_action:
              methods:
                - "POST"
              paths:
                - "/api/v2/slack/action/testteam/echobot"
          bindings:
            "envoy":
              - "slack_api"
            "echobot.*":
              - "echobot_slack_action"
    """
    envoy_identity = request.headers.get(header)
    if envoy_identity is None:
        return False
    bindings = settings.AUTHORIZATION.get('bindings', {})
    for subject, permissions in bindings.items():
        if _match_subject(envoy_identity, subject):
            for permission in permissions:
                if _check_permission(permission):
                    return True
    logger.warning(
        'Received an unauthorized request from={} to endpoint={}'.format(
            envoy_identity,
            request.path
        )
    )
    return False
