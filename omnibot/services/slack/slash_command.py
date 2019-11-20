import logging

from omnibot.services import slack
from omnibot.services.slack import parser

logger = logging.getLogger(__name__)


class SlashCommand(object):
    """
    Class for representing a parsed slack SlashCommand.
    """

    def __init__(self, bot, command, event_trace):
        self._event_trace = event_trace
        self._command = command
        self._payload = {}
        self._payload['omnibot_payload_type'] = 'slash_command'
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
        self._payload['enterprise_id'] = self._command.get('enterprise_id')
        self._payload['enterprise_name'] = self._command.get('enterprise_name')
        self._payload['command'] = self._command['command']
        self._payload['response_url'] = self._command['response_url']
        self._payload['trigger_id'] = self._command['trigger_id']
        self._payload['user_id'] = self._command.get('user_id')
        if self.user_id:
            self._payload['parsed_user'] = slack.get_user(
                self.bot,
                self.user_id
            )
        else:
            self._payload['parsed_user'] = None
        try:
            self._payload['text'] = command['text']
        except Exception:
            logger.error(
                'Slash command is missing text attribute.',
                extra=self.event_trace
            )
            raise
        self._payload['parsed_text'] = self.text
        self._payload['channel_id'] = command['channel_id']
        self._event_trace['channel_id'] = self.channel_id
        self._payload['channel'] = slack.get_channel(
            self.bot,
            self.channel_id
        )
        if not self.channel:
            logger.error(
                'Failed to fetch channel from channel_id.',
                extra=self.event_trace
            )

        self._parse_payload()

    def _parse_payload(self):
        try:
            self._payload['users'] = parser.extract_users(self.text, self.bot)
            self._payload['parsed_text'] = parser.replace_users(
                self.parsed_text,
                self.users
            )
        except Exception:
            logger.exception(
                'Failed to extract user info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['channels'] = parser.extract_channels(
                self.text,
                self.bot
            )
            self._payload['parsed_text'] = parser.replace_channels(
                self.parsed_text,
                self.channels
            )
        except Exception:
            logger.exception(
                'Failed to extract channel info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['subteams'] = parser.extract_subteams(
                self.text,
                self.bot
            )
        except Exception:
            logger.exception(
                'Failed to extract subteam info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['specials'] = parser.extract_specials(self.text)
            self._payload['parsed_text'] = parser.replace_specials(
                self.parsed_text,
                self.specials
            )
        except Exception:
            logger.exception(
                'Failed to extract special info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['emojis'] = parser.extract_emojis(self.text)
        except Exception:
            logger.exception(
                'Failed to extract emoji info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['emails'] = parser.extract_emails(self.text)
            self._payload['parsed_text'] = parser.replace_emails(
                self.parsed_text,
                self.emails
            )
        except Exception:
            logger.exception(
                'Failed to extract email info from text.',
                exc_info=True,
                extra=self.event_trace
            )
        try:
            self._payload['urls'] = parser.extract_urls(self.text)
            self._payload['parsed_text'] = parser.replace_urls(
                self.parsed_text,
                self.urls
            )
        except Exception:
            logger.exception(
                'Failed to extract url info from text.',
                exc_info=True,
                extra=self.event_trace
            )

    @property
    def command(self):
        return self._payload['command']

    @property
    def response_url(self):
        return self._payload['response_url']

    @property
    def text(self):
        return self._payload['text']

    @property
    def parsed_text(self):
        return self._payload['parsed_text']

    @property
    def channel_id(self):
        return self._payload.get('channel_id')

    @property
    def channel(self):
        return self._payload.get('channel', {})

    @property
    def user_id(self):
        return self._payload['user_id']

    @property
    def trigger_id(self):
        return self._payload['trigger_id']

    @property
    def team(self):
        return self._payload['team']

    @property
    def bot(self):
        """
        The bot associated with the app that received this message from the
        slash command api. To get info about a bot that may have sent
        this message, see bot_id.
        """
        return self._bot

    @property
    def bot_id(self):
        """
        The bot_id associated with the message, if the message if from a bot.
        If this message isn't from a bot, this will return None.
        """
        return self._command.get('bot_id')

    @property
    def enterprise_id(self):
        return self._payload['enterprise_id']

    @property
    def enterprise_name(self):
        return self._payload['enterprise_name']

    @property
    def channels(self):
        return self._payload.get('channels', {})

    @property
    def users(self):
        return self._payload.get('users', {})

    @property
    def specials(self):
        return self._payload.get('specials', {})

    @property
    def emails(self):
        return self._payload.get('emails', {})

    @property
    def urls(self):
        return self._payload.get('urls', {})

    @property
    def payload(self):
        return self._payload

    @property
    def event_trace(self):
        return self._event_trace
