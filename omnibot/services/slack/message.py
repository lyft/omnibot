import logging

from omnibot.services import stats
from omnibot.services import slack
from omnibot.services.slack import parser

logger = logging.getLogger(__name__)


class Message(object):
    """
    Class for representing a parsed slack message.
    """

    def __init__(self, bot, event, event_trace):
        self._event_trace = event_trace
        self.event = event
        self._match = None
        self._payload = {}
        self._payload['omnibot_payload_type'] = 'message'
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
        self._payload['ts'] = event['ts']
        self._payload['thread_ts'] = event.get('thread_ts')
        self._check_unsupported()
        self._payload['user'] = event.get('user')
        if self.user:
            self._payload['parsed_user'] = slack.get_user(self.bot, self.user)
        elif self.bot_id:
            # TODO: call get_bot
            self._payload['parsed_user'] = None
        else:
            self._payload['parsed_user'] = None
        try:
            self._payload['text'] = event['text']
        except Exception:
            logger.error(
                'Message event is missing text attribute.',
                extra=self.event_trace
            )
            raise
        self._payload['parsed_text'] = self.text
        self._payload['channel_id'] = event['channel']
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

    def _check_unsupported(self):
        # TODO: make the ignores configurable, but have a default list
        # Ignore self
        # Ignore bots
        unsupported = False
        if self.bot_id:
            logger.debug('ignoring message from bot', extra=self.event_trace)
            unsupported = True
        # Ignore threads
        elif self.thread_ts:
            logger.debug('ignoring thread message', extra=self.event_trace)
            unsupported = True
        # For now, ignore all event subtypes
        elif self.subtype:
            logger.debug(
                'ignoring message with subtype: {}'.format(self.subtype),
                extra=self.event_trace
            )
            unsupported = True
        if unsupported:
            statsd = stats.get_statsd_client()
            statsd.incr('event.unsupported')
            raise MessageUnsupportedError()

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
        try:
            self._payload['directed'] = parser.extract_mentions(
                # We match mentioned and directed against parsed users, not
                # against raw users.
                self.parsed_text,
                self.bot,
                self.channel
            )
        except Exception:
            logger.exception(
                'Failed to extract mentions from text.',
                exc_info=True,
                extra=self.event_trace
            )
        self._payload['mentioned'] = False
        for user_id, user_name in self.users.items():
            if self.bot.name == user_name:
                self._payload['mentioned'] = True
        try:
            self._payload['command_text'] = parser.extract_command(
                # Similar to mentions above, we find the command text
                # from pre-parsed text for users, not against raw users.
                self.parsed_text,
                self.bot
            )
        except Exception:
            logger.exception(
                'Failed to extract command_text from text.',
                exc_info=True,
                extra=self.event_trace
            )

    @property
    def subtype(self):
        return self.event.get('subtype')

    @property
    def text(self):
        return self._payload['text']

    @property
    def parsed_text(self):
        return self._payload['parsed_text']

    @property
    def command_text(self):
        return self._payload.get('command_text')

    @property
    def directed(self):
        return self._payload.get('directed', False)

    @property
    def mentioned(self):
        return self._payload.get('mentioned', False)

    @property
    def channel_id(self):
        return self._payload.get('channel_id')

    @property
    def channel(self):
        return self._payload.get('channel', {})

    @property
    def user(self):
        return self._payload['user']

    @property
    def ts(self):
        return self._payload['ts']

    @property
    def thread_ts(self):
        return self._payload['thread_ts']

    @property
    def team(self):
        return self._payload['team']

    @property
    def bot(self):
        """
        The bot associated with the app that received this message from the
        event subscription api. To get info about a bot that may have sent
        this message, see bot_id.
        """
        return self._bot

    @property
    def bot_id(self):
        """
        The bot_id associated with the message, if the message if from a bot.
        If this message isn't from a bot, this will return None.
        """
        return self.event.get('bot_id')

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
    def match_type(self):
        return self._payload.get('match_type')

    @property
    def match(self):
        return self._match

    @property
    def payload(self):
        return self._payload

    @property
    def event_trace(self):
        return self._event_trace

    def set_match(self, match_type, match):
        self._payload['match_type'] = match_type
        self._match = match
        if match_type == 'command':
            self._payload['command'] = match
            self._payload['args'] = self.command_text[len(match):].strip()
        elif match_type == 'regex':
            self._payload['regex'] = match


class MessageUnsupportedError(Exception):
    pass
