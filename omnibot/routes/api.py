"""
API module for omnibot, to handle events from slack, or to handle
service-to-service calls.

Endpoints in this module may be access controlled through the authorization
configuration; see documentation on checks:

* :func:`omnibot.authnz:enforce_checks`
"""
from __future__ import absolute_import
import json
import logging
import time
from functools import wraps

from flask import (
    Blueprint,
    jsonify,
    request,
    abort
)

from omnibot import authnz
from omnibot.processor import parse_kwargs
from omnibot.services import sqs
from omnibot.services import stats
from omnibot.services import slack
from omnibot.services.slack.team import Team
from omnibot.services.slack.team import TeamInitializationError
from omnibot.services.slack.bot import Bot
from omnibot.services.slack.bot import BotInitializationError
from omnibot.utils import get_callback_id

logger = logging.getLogger(__name__)

blueprint = Blueprint('api', __name__)


def verify_bot(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        bot_name = request.view_args.get('bot_name')
        team_name = request.view_args.get('team_name')
        try:
            team = Team.get_team_by_name(team_name)
        except TeamInitializationError:
            logger.warning('Failed to validate bot={} team={}.'.format(
                bot_name,
                team_name
            ))
            return abort(404)
        try:
            Bot.get_bot_by_name(team, bot_name)
        except BotInitializationError:
            logger.warning('Failed to validate bot={} team={}.'.format(
                bot_name,
                team_name
            ))
            return abort(404)
        return f(*args, **kwargs)
    return decorated


@blueprint.route('/healthcheck')
def healthcheck():
    # The healthcheck returns status code 200
    return 'OK'


@blueprint.route('/api/v1/slack/event', methods=['POST'])
@authnz.enforce_checks
def slack_event():
    """
    Handle event subscription API webhooks from slack.
    """
    event = request.json
    logger.debug(event)
    # Every event should have a validation token
    if 'token' not in event:
        msg = 'No verification token in event.'
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    # url_verification events don't contain info about team_id or api_app_id,
    # annoyingly, so we need to special case this to validate the token
    # against all configured apps.
    if event.get('type') == 'url_verification':
        try:
            Bot.get_bot_by_verification_token(event['token'])
        except BotInitializationError:
            msg = 'url_verification failed.'
            logger.error(msg)
            return jsonify({'status': 'failure', 'error': msg}), 403
        return jsonify({'challenge': event['challenge']})
    api_app_id = event.get('api_app_id')
    if api_app_id is None:
        msg = 'No api_app_id in event.'
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    team_id = event.get('team_id')
    if team_id is None:
        msg = 'No team_id in event.'
        logger.error('{}, App={}'.format(msg, api_app_id))
        return jsonify({'status': 'failure', 'error': msg}), 403
    try:
        team = Team.get_team_by_id(team_id)
    except TeamInitializationError:
        msg = 'Unsupported team'
        logger.warning('{}={}, App={}'.format(msg, team_id, api_app_id))
        return jsonify({'status': 'failure', 'error': msg}), 403
    try:
        bot = Bot.get_bot_by_bot_id(team, api_app_id)
    except BotInitializationError:
        msg = 'Unsupported bot'
        logger.info('{}={}'.format(msg, api_app_id))
        return jsonify({'status': 'ignored', 'warning': msg}), 200
    if event['token'] != bot.verification_token:
        msg = 'Incorrect verification token in event for bot_id'
        logger.error('{}={}'.format(msg, bot.bot_id))
        return jsonify({'status': 'failure', 'error': msg}), 403
    if 'event' not in event:
        msg = 'Request does not have an event. Processing will not proceed!'
        logger.error('{}. Bot={}'.format(msg, bot.bot_id))
        return jsonify({'status': 'failure', 'error': msg}), 403
    try:
        instrument_event(bot, event)
    except Exception:
        logger.exception('Could not instrument request. Bot={}'.format(bot.bot_id))
    try:
        queue_event(bot, event, 'event')
    except Exception:
        logger.exception('Could not queue request. Bot={}'.format(bot.bot_id))
        return jsonify({'status': 'failure'}), 500
    return jsonify({'status': 'success'}), 200


@blueprint.route('/api/v1/slack/slash_command', methods=['POST'])
@authnz.enforce_checks
def slack_slash_command():
    # Slack sends slash commands as application/x-www-form-urlencoded
    command = request.form.to_dict()
    logger.debug(command)
    # Every event should have a validation token
    if 'token' not in command:
        msg = 'No verification token in slash command.'
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    if 'team_id' not in command:
        msg = 'No team_id in slash command.'
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    try:
        team = Team.get_team_by_id(command['team_id'])
    except TeamInitializationError:
        msg = 'Unsupported team'
        logger.warning('{}={}'.format(msg, command['team_id']))
        return jsonify({'status': 'failure', 'error': msg}), 403
    # Slash commands annoyingly don't send an app id, so we need to
    # verify
    try:
        bot = Bot.get_bot_by_verification_token(command['token'])
    except BotInitializationError:
        msg = (
            'Token sent with slash command does not match any configured app.'
        )
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    if team.team_id != bot.team.team_id:
        # This should never happen, but let's be paranoid.
        msg = (
            'Token sent with slash command does not match team in event.'
        )
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    handler_found = None
    for slash_handler in bot.slash_command_handlers:
        if command['command'] == slash_handler.get('command'):
            handler_found = slash_handler
            break
    if not handler_found:
        msg = ('This slash command does not have any omnibot handler'
               ' associated with it.')
        logger.error(msg)
        return jsonify({'response_type': 'ephemeral', 'text': msg}), 200
    # To avoid needing to look the bot up from its token when the dequeue this
    # command,:let's extend the payload with the bot id
    command['omnibot_bot_id'] = bot.bot_id
    # We can't instrument slash commands, because they don't have ts info.
    # TODO: investigate if we can parse the trigger ID; it's possible part
    # of that is a timestamp
    try:
        # If there's no callbacks defined for this slash command, we
        # can skip enqueuing it, since the workers will just discard it.
        if handler_found.get('callbacks'):
            queue_event(bot, command, 'slash_command')
    except Exception:
        msg = 'Could not queue slash command.'
        logger.exception(msg)
        return jsonify({'status': 'failure', 'error': msg}), 500
    if handler_found.get('dialog'):
        _perform_action(bot, {
            'action': 'dialog.open',
            'kwargs': {
                'dialog': handler_found['dialog'],
                'trigger_id': command['trigger_id']
            }
        })
    return _get_write_message_response(handler_found), 200


@blueprint.route('/api/v1/slack/interactive', methods=['POST'])
@authnz.enforce_checks
def slack_interactive_component():
    # Slack sends interactive components as application/x-www-form-urlencoded,
    # json encoded inside of the payload field. What a whacky API.
    component = json.loads(request.form.to_dict().get('payload', {}))
    logger.debug(component)
    if (
        component.get('type') not in [
            'interactive_message',
            'message_action',
            'dialog_submission',
            'block_actions',
        ]
    ):
        msg = ('Unsupported type={} in interactive'
               ' component.'.format(component.get('type')))
        logger.warning(msg)
        return jsonify({'status': 'failure', 'error': msg}), 400
    # Every event should have a validation token
    if 'token' not in component:
        msg = 'No verification token in interactive component.'
        logger.warning(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    if not component.get('team', {}).get('id'):
        msg = 'No team id in interactive component.'
        logger.warning(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    try:
        team = Team.get_team_by_id(component['team']['id'])
    except TeamInitializationError:
        msg = 'Unsupported team'
        logger.warning('{}={}'.format(msg, component['team']['id']))
        return jsonify({'status': 'failure', 'error': msg}), 403
    # interactive components annoyingly don't send an app id, so we need
    # to verify
    try:
        bot = Bot.get_bot_by_verification_token(component['token'])
    except BotInitializationError:
        msg = ('Token sent with interactive component does not match any'
               ' configured app.')
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    if team.team_id != bot.team.team_id:
        # This should never happen, but let's be paranoid.
        msg = (
            'Token sent with slash command does not match team in event.'
        )
        logger.error(msg)
        return jsonify({'status': 'failure', 'error': msg}), 403
    handler_found = None
    for handler in bot.interactive_component_handlers:
        if get_callback_id(component) == handler.get('callback_id'):
            handler_found = handler
            break
    if not handler_found:
        msg = ('This interactive component does not have any omnibot handler'
               ' associated with it.')
        logger.error(msg)
        return jsonify({'response_type': 'ephemeral', 'text': msg}), 200
    # To avoid needing to look the bot up from its token when the dequeue this
    # command,:let's extend the payload with the bot id
    component['omnibot_bot_id'] = bot.bot_id
    # TODO: Use action_ts to instrument event
    try:
        # If there's no callbacks defined for this interactive component, we
        # can skip enqueuing it, since the workers will just discard it.
        if handler_found.get('callbacks'):
            queue_event(bot, component, 'interactive_component')
    except Exception:
        msg = 'Could not queue interactive component.'
        logger.exception(msg)
        return jsonify({'status': 'failure', 'error': msg}), 500
    # Open a dialog, if we have a trigger ID, and a dialog is defined for this
    # handler. Not all interactive components have a trigger ID.
    if component.get('trigger_id') and handler_found.get('dialog'):
        _perform_action(bot, {
            'action': 'dialog.open',
            'kwargs': {
                'dialog': handler_found['dialog'],
                'trigger_id': component['trigger_id']
            }
        })
    if component['type'] in ['dialog_submission']:
        return '', 200
    elif handler_found.get('no_message_response'):
        return '', 200
    else:
        return _get_write_message_response(handler_found), 200


def _get_write_message_response(handler):
    canned_response = handler.get('canned_response')
    response_type = handler.get('response_type', 'ephemeral')
    response = {}
    if canned_response:
        response['text'] = canned_response
        response['response_type'] = response_type
    else:
        # If we aren't sending back text, we can only send back a response
        # type if it's in_channel, or the slash command will respond with an
        # error every time.
        if response_type == 'in_channel':
            response['response_type'] = response_type
    # We can only send back a json payload if we have items in it, or slack
    # sends errors in the slash command.
    if response:
        return jsonify(response)
    else:
        return ''


def instrument_event(bot, event):
    statsd = stats.get_statsd_client()
    retry = request.headers.get(
        'X-Slack-Retry-Num',
        default=0,
        type=int
    )
    retry_reason = request.headers.get(
        'X-Slack-Retry-Reason',
        default='',
        type=str
    )
    event_info = event['event']
    event_sent_time_ms = int(float(event_info['event_ts']) * 1000)
    now = int(time.time() * 1000)
    latency = now - event_sent_time_ms
    if retry > 0:
        statsd.timing('pre_sqs_delivery_retry_latency', latency)
    else:
        statsd.timing('pre_sqs_delivery_latency', latency)
    if latency > 20000:
        logger.warning(
            'Event is greater than 20s delayed in'
            ' delivery ({} ms)'.format(latency),
            extra={
                'event_ts': event_info['event_ts'],
                'app_id': event['api_app_id'],
                'team_id': event['team_id'],
                'event_type': event_info['type'],
                'bot_receiver': bot.name,
                'retry': retry
            }
        )
    if retry_reason:
        logger.warning(
            'Incoming message is a retry: reason="{}"'.format(retry_reason)
        )


def queue_event(bot, event, event_type):
    statsd = stats.get_statsd_client()
    sqs_client = sqs.get_client()
    sqs_client.send_message(
        QueueUrl=sqs.get_queue_url(),
        MessageBody=json.dumps({
            'event': event
        }),
        MessageAttributes={
            # Add a version, so we know how to parse this in the receiver when
            # we make message schema changes.
            'version': {
                'DataType': 'Number',
                # Seems SQS uses StringValue for Number type... We'll cast
                # this on the receiver end.
                'StringValue': '2'
            },
            # Specify the type of SQS message, so we can handle more than just
            # the event subscription API.
            'type': {
                'DataType': 'String',
                'StringValue': event_type
            }
        }
    )
    statsd.incr('sqs.sent')
    statsd.incr('sqs.{}.sent'.format(bot.name))


@blueprint.route(
    '/api/v1/slack/get_team/<team_name>',
    methods=['GET']
)
@authnz.enforce_checks
def get_team_id_by_name(team_name):
    """
    Get a team_id, from its `team_name`.

    .. :quickref: Team ID; Get team_id from team_name

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/slack/get_team/myteam HTTP/1.1

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {"team_id": "T123456"}

    :param team_name: The team to search for this user, as configured in
                      omnibot.
    :type team_name: str
    :reqheader x-envoy-internal: Header that indicates whether or not this
                                 request is coming from an internal service
                                 or not. This is auto-set by envoy and doesn't
                                 need to be explicitly set.
    :resheader Content-Type: application/json
    :statuscode 200: success
    :statuscode 404: team is not configured
    """
    logger.debug('Getting team id for team={}.'.format(team_name))
    try:
        team = Team.get_team_by_name(team_name)
        return jsonify({'team_id': team.team_id})
    except TeamInitializationError:
        return jsonify(
            {'error': 'provided team_name is not configured.'}
        ), 404


@blueprint.route(
    '/api/v1/slack/get_user/<team_name>/<bot_name>/<email>',
    methods=['GET']
)
@authnz.enforce_checks
@verify_bot
def get_user_v2(team_name, bot_name, email):
    """
    Returns basic user information, for the provided `email` in the `team_name`
    using the specified `bot_name`.

    .. :quickref: User; Get a user from a team, via their email

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/slack/get_user/myteam/mybot/user@example.com HTTP/1.1

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {"email": "user@example.com", "name": "Test User", "team_id": "T123456",
        "user_id": "U123ABC"}

    :param team_name: The team to search for this user, as configured in
                      omnibot.
    :type team_name: str
    :param bot_name: The bot to use for the request, as configured in omnibot.
    :type bot_name: str
    :param email: The email address of the user to get.
    :type email: str
    :reqheader x-envoy-internal: Header that indicates whether or not this
                                 request is coming from an internal service
                                 or not. This is auto-set by envoy and doesn't
                                 need to be explicitly set.
    :resheader Content-Type: application/json
    :statuscode 200: success
    :statuscode 404: user with specified email could not be found using the
                     specified bot.
    """
    logger.debug(
        'Getting user for team={} bot={} email={}.'.format(
            team_name,
            bot_name,
            email
        )
    )
    try:
        team = Team.get_team_by_name(team_name)
    except TeamInitializationError:
        return jsonify({'error': 'provided team name was not found.'}), 404
    try:
        bot = Bot.get_bot_by_name(team, bot_name)
    except BotInitializationError:
        return jsonify({'error': 'provided bot name was not found.'}), 404
    user = slack.get_user_by_email(bot, email)
    name = slack.get_name_from_user(user)
    return jsonify({
        'user': {
            'email': user['profile']['email'],
            'name': name,
            'team_id': team.team_id,
            'user_id': user['id']
        }
    })


@blueprint.route(
    '/api/v1/slack/get_channel/<team_name>/<bot_name>/<channel_name>',
    methods=['GET']
)
@authnz.enforce_checks
@verify_bot
def get_channel_by_name(team_name, bot_name, channel_name):
    """
    Returns a channel object from slack, for the provided `channel_name` in
    the `team_name` using the specified `bot_name`.

    .. :quickref: Channel; Get a channel from a team, via the channel_name

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/slack/get_channel/myteam/mybot/general HTTP/1.1

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "channel": {
           "id": "C4VQ6NUNN",
           "name": "general",
           "is_channel": true,
           "created": 1491515285,
           "creator": "U4WF56QGP",
           "is_archived": false,
           "is_general": true,
           "unlinked": 0,
           "name_normalized": "general",
           "is_shared": false,
           "is_org_shared": false,
           "is_member": false,
           "is_private": false,
           "is_mpim": false,
           "members": [
             "U4WF56QGP",
             "U6HQQ19EC",
             "U6J3LTKSQ",
             "U6J4EGP44",
             "U6JDF1JBU",
             "U6JEGTFDZ",
             "U6JERPMJ7",
             "U6JG691MJ",
             "U6JGEQ0J0",
             "U6SAVUK44",
             "U750C7B37",
             "U7DH0H802"
           ],
           "topic": {
             "value": "test123",
             "creator": "U6J3LTKSQ",
             "last_set": 1507156612
           },
           "purpose": {
             "value": "This channel is for team-wide communication."
             "creator": "",
             "last_set": 0
           },
           "previous_names": [],
           "num_members": 9
         }
      }

    :param team_name: The team to search for this channel, as configured in
                      omnibot.
    :type team_name: str
    :param bot_name: The bot to use for the request, as configured in omnibot.
    :type bot_name: str
    :param channel_name: The name of the channel to get.
    :type channel_name: str
    :reqheader x-envoy-internal: Header that indicates whether or not this
                                 request is coming from an internal service
                                 or not. This is auto-set by envoy and doesn't
                                 need to be explicitly set.
    :resheader Content-Type: application/json
    :statuscode 200: success
    :statuscode 404: channel with specified channel_name could not be found
                     in the specified team using the specified bot.
    """
    logger.debug(
        'Getting channel for team={} bot={} channel={}.'.format(
            team_name,
            bot_name,
            channel_name
        )
    )
    try:
        team = Team.get_team_by_name(team_name)
    except TeamInitializationError:
        return jsonify({'error': 'provided team name was not found.'}), 404
    try:
        bot = Bot.get_bot_by_name(team, bot_name)
    except BotInitializationError:
        return jsonify({'error': 'provided bot name was not found.'}), 404
    channel = slack.get_channel_by_name(bot, channel_name)
    if channel is None:
        logger.debug(
            'Failed to get channel for team={} bot={} channel={}.'.format(
                team_name,
                bot_name,
                channel_name
            )
        )
        return jsonify({'error': 'provided channel_name was not found.'}), 404
    return jsonify(channel)


def _perform_action(bot, data):
    for arg in ['action', 'kwargs']:
        if arg not in data:
            return {
                'ok': False,
                'error': '{} not provided in payload'.format(arg)
            }
    action = data['action']
    kwargs = data['kwargs']
    logger.debug(
        'Posting for team={} bot={} action={}'.format(
            bot.team.name,
            bot.name,
            action
        )
    )
    parse_kwargs(kwargs, bot)
    ret = slack.client(bot, client_type='oauth_bot').api_call(
        action,
        **kwargs
    )
    logger.debug(ret)
    if not ret['ok']:
        if ret.get('error') in ['missing_scope', 'not_allowed_token_type']:
            logger.warning(
                'action={} failed in post_slack, attempting as user.'.format(
                    action
                )
            )
            try:
                ret = slack.client(bot, client_type='oauth').api_call(
                    action,
                    **kwargs
                )
            except json.decoder.JSONDecodeError:
                logger.exception(
                    'JSON decode failure when parsing kwargs={}'.format(
                        kwargs
                    )
                )
                return {'ok': False}
            logger.debug(ret)
            if not ret['ok']:
                logger.error(
                    'action={} failed in post_slack: ret={}'.format(
                        action,
                        ret
                    )
                )
        else:
            logger.error(
                'action={} failed in post_slack: ret={}'.format(
                    action,
                    ret
                )
            )
    return ret


@blueprint.route(
    '/api/v2/slack/action/<team_name>/<bot_name>',
    methods=['POST']
)
@authnz.enforce_checks
@verify_bot
def slack_action_v2(team_name, bot_name):
    """
    Perform an action against slack, as the provided `bot_name` in the
    provided `team_name`.

    .. :quickref: SlackAction; Perform a slack action in a specified team as
                  a specified bot.

    **Example request**:

    .. sourcecode:: http

       POST /api/v1/slack/action/myteam/mybot HTTP/1.1
       Content-Type: application/json

       {
         "action": "chat.postMessage",
         "kwargs": {
           "channel": "test-omnibot",
           "text": "@example see #general and use @here",
           "as_user": true,
           "omnibot_parse": {
             "text": ["channels", "users", "specials"]
           }
         }
       }

    :<json string action: slack api action to perform. example:
                          `chat.postMessage`
    :<json dict kwargs: keyword arguments you'd pass into the associated
                        slack api action. example:
                        `"text": "@example see #general and use @here"`
    :<json dict omnibot_parse: The keyword argument you'd like omnibot to
                               parse, with a list of things to parse. example:
                               {"text": ["channels", "users", "specials"]}

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "channel": "C12345",
         "message": {
           "bot_id": "B456123",
           "subtype": "bot_message",
           "text": "<@UABC123|example> see <#C12345|general> and use <!here|here>",
           "ts": "1523557397.000335",
           "type": "message",
           "username": "mybot"
         },
         "ok": true,
         "ts": "1523557397.000335"
       }

    :param team_name: The team to perform this action against, as configured in
                      omnibot.
    :type team_name: str
    :param bot_name: The bot to use for the request, as configured in omnibot.
    :type bot_name: str
    :reqheader x-envoy-internal: Header that indicates whether or not this
                                 request is coming from an internal service
                                 or not. This is auto-set by envoy and doesn't
                                 need to be explicitly set.
    :resheader Content-Type: application/json
    :statuscode 200: success
    :statuscode 400: slack call returned a non-OK status
    """
    data = request.json
    try:
        team = Team.get_team_by_name(team_name)
    except TeamInitializationError:
        return jsonify({'error': 'provided team name was not found.'}), 404
    try:
        bot = Bot.get_bot_by_name(team, bot_name)
    except BotInitializationError:
        return jsonify({'error': 'provided bot name was not found.'}), 404
    ret = _perform_action(bot, data)
    if ret['ok']:
        return jsonify(ret), 200
    else:
        return jsonify(ret), 400


@blueprint.route(
    '/api/v1/slack/get_ims/<team_name>/<bot_name>',
    methods=['GET']
)
@authnz.enforce_checks
@verify_bot
def get_bot_ims(team_name, bot_name):
    """
    Returns list of IMs (DMs with a bot), for the provided
    `bot_name` and `team_name`.

    .. :quickref: Get a list of IMs for a bot within a team

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/slack/get_ims/myteam/mybot

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {"ims":
            [
                {
                    "id": 'D1234567',
                    "created": 1518129625,
                    "is_im": true,
                    "is_org_shared": true,
                    "user": "U1234567"
                    "is_user_deleted": false,
                    "priority": 0.01234567
                }
            ]
        }

    :param team_name: The team to search for this user, as configured in
                      omnibot.
    :type team_name: str
    :param bot_name: The bot to use for the request, as configured in omnibot.
    :type bot_name: str
    """
    try:
        team = Team.get_team_by_name(team_name)
    except TeamInitializationError:
        return jsonify({'error': 'provided team name was not found.'}), 404
    try:
        bot = Bot.get_bot_by_name(team, bot_name)
    except BotInitializationError:
        return jsonify({'error': 'provided bot name was not found.'}), 404
    raw_ims = slack.get_ims(bot)
    ims = []
    for im in raw_ims:
        # each im is a tuple where im[0] is the channel id and im[1] is the im object
        ims.append(json.loads(im[1]))
    return jsonify(
        {'ims': ims}
    )


@blueprint.route(
    '/api/v1/slack/send_im/<team_name>/<bot_name>/<email>', methods=['POST']
)
@authnz.enforce_checks
@verify_bot
def send_bot_im(team_name, bot_name, email):
    """
    Sends a message as a bot user to an IM (direct message) channel
    between a team member and a bot user,
    for the provided `team_name`, `bot_name`, and `email`.

    .. :quickref: Send an IM message between bot and user

    **Example request**:

    .. sourcecode:: http

       GET /api/v1/slack/send_im/myteam/mybot/myemail@example.com

    **Example response**:

    .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
            "channel": "DC1234567",
            "message": {
                "bot_id": "BC1234567",
                "subtype": "bot_message",
                "text": "HI!",
                "ts": "1538593287.000100",
                "type": "message",
                "username": "mybot"
            },
            "ok": true,
            "ts": "1538593287.000100"
        }

    :param team_name: The team to search for the given bot,
                      as configured in omnibot.
    :type team_name: str
    :param bot_name: The bot sending the IM to the user,
                     as configured in omnibot.
    :type bot_name: str
    :param email: The email address of user to send message to
    :type email: str

    :resheader Content-Type: application/json
    :statuscode 200: success
    :statuscode 400: slack call returned a non-OK status
    :statuscode 404: team, bot, IM unable to be found,
                     or user deleted from slack team
    """
    data = request.json
    try:
        team = Team.get_team_by_name(team_name)
        bot = Bot.get_bot_by_name(team, bot_name)
    except TeamInitializationError:
        return jsonify({'error': 'provided team name was not found.',
                        'team_name': team_name,
                        'bot_name': bot_name,
                        'email': email
                        }), 404
    except BotInitializationError:
        return jsonify({'error': 'provided bot name was not found.',
                        'team_name': team_name,
                        'bot_name': bot_name,
                        'email': email
                        }), 404
    user = slack.get_user_by_email(bot, email)
    if not user:
        return jsonify({'error': 'unable to find slack user for given email.',
                        'team_name': team_name,
                        'bot_name': bot_name,
                        'email': email
                        }), 404
    im_id = slack.get_im_channel_id(bot, user['id'])
    if im_id is None:
        return jsonify({'error': 'unable to find IM channel.',
                        'team_name': team_name,
                        'bot_name': bot_name,
                        'email': email
                        }), 404
    data['kwargs']['channel'] = im_id
    ret = _perform_action(bot, data)
    if ret['ok']:
        return jsonify(ret), 200
    else:
        return jsonify(ret), 400
