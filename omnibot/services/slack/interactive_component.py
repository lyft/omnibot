import logging

from omnibot.services import slack
from omnibot.services.slack import parser
from omnibot.utils import get_callback_id

logger = logging.getLogger(__name__)


class InteractiveComponent(object):
    """
    Class for representing a parsed slack InteractiveComponent.
    """

    def __init__(self, bot, component, event_trace):
        self._event_trace = event_trace
        self._payload = {}
        self._payload['omnibot_payload_type'] = 'interactive_component'
        self._bot = bot
        # The bot object has data we don't want to pass to downstreams, so
        # in the payload, we just store specific bot data.
        self._payload['bot'] = {
            'name': bot.name,
            'bot_id': bot.bot_id
        }
        # For future safety sake, we'll do the same for the team.
        self._payload['team'] = {
            'name': bot.team.name,
            'team_id': bot.team.team_id
        }
        self._payload['type'] = component['type']
        self._payload['callback_id'] = get_callback_id(component)
        self._payload['action_ts'] = component.get('action_ts')
        self._payload['message_ts'] = component.get('message_ts')
        self._payload['trigger_id'] = component.get('trigger_id')
        self._payload['response_url'] = component['response_url']
        self._payload['original_message'] = component.get('original_message')
        self._payload['state'] = component.get('state')
        self._payload['user'] = component.get('user')
        if self.user:
            self._payload['parsed_user'] = slack.get_user(
                self.bot,
                self.user['id']
            )
        self._payload['channel'] = component.get('channel')
        if self.channel:
            self._event_trace['channel_id'] = self.channel['id']
            self._payload['parsed_channel'] = slack.get_channel(
                self.bot,
                self.channel['id']
            )
        self._payload['message'] = component.get('message')
        if self.message:
            self._parse_message()
        self._payload['submission'] = component.get('submission')
        self._payload['actions'] = component.get('actions')

    def _parse_message(self):
        if self.message.get('user'):
            self._payload['message']['parsed_user'] = slack.get_user(
                self.bot,
                self.message['user']
            )
        elif self.message.get('bot_id'):
            # TODO: call get_bot
            self._payload['message']['parsed_user'] = None
        else:
            self._payload['message']['parsed_user'] = None
        try:
            self._payload['message']['users'] = parser.extract_users(
                self.message['text'],
                self.bot
            )
            self._payload['message']['parsed_text'] = parser.replace_users(
                self.message['text'],
                self.message['users']
            )
        except Exception:
            logger.exception(
                'Failed to extract user info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['message']['channels'] = parser.extract_channels(
                self.message['parsed_text'],
                self.bot
            )
            self._payload['message']['parsed_text'] = parser.replace_channels(
                self.message['parsed_text'],
                self.message['channels']
            )
        except Exception:
            logger.exception(
                'Failed to extract channel info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['message']['subteams'] = parser.extract_subteams(
                self.message['text'],
                self.bot
            )
        except Exception:
            logger.exception(
                'Failed to extract subteam info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['message']['specials'] = parser.extract_specials(
                self.message['text']
            )
            self._payload['message']['parsed_text'] = parser.replace_specials(
                self.message['parsed_text'],
                self.message['specials']
            )
        except Exception:
            logger.exception(
                'Failed to extract special info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['message']['emojis'] = parser.extract_emojis(
                self.message['text']
            )
        except Exception:
            logger.exception(
                'Failed to extract emoji info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['message']['emails'] = parser.extract_emails(
                self.message['text']
            )
            self._payload['message']['parsed_text'] = parser.replace_emails(
                self.message['parsed_text'],
                self.message['emails']
            )
        except Exception:
            logger.exception(
                'Failed to extract email info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['message']['urls'] = parser.extract_urls(
                self.message['text']
            )
            self._payload['message']['parsed_text'] = parser.replace_urls(
                self.message['parsed_text'],
                self.message['urls']
            )
        except Exception:
            logger.exception(
                'Failed to extract url info from text.',
                exc_info=True,
                extra=self.event_trace
            )

    @property
    def component_type(self):
        return self._payload['type']

    @property
    def callback_id(self):
        return self._payload['callback_id']

    @property
    def action_ts(self):
        return self._payload['action_ts']

    @property
    def trigger_id(self):
        return self._payload['trigger_id']

    @property
    def response_url(self):
        return self._payload['response_url']

    @property
    def message(self):
        return self._payload['message']

    @property
    def submission(self):
        return self._payload['submission']

    @property
    def actions(self):
        return self._payload['actions']

    @property
    def channel(self):
        return self._payload['channel']

    @property
    def channel_id(self):
        return self._payload['channel']['id']

    @property
    def parsed_channel(self):
        return self._payload.get('parsed_channel')

    @property
    def user(self):
        return self._payload['user']

    @property
    def parsed_user(self):
        return self._payload.get('parsed_user')

    @property
    def team(self):
        return self._payload['team']

    @property
    def bot(self):
        """
        The bot associated with the app that received this message from the
        slash component api. To get info about a bot that may have sent
        this message, see bot_id.
        """
        return self._bot

    @property
    def payload(self):
        return self._payload

    @property
    def event_trace(self):
        return self._event_trace
