from omnibot import logging
from omnibot.services import slack
from omnibot.services import stats
from omnibot.services.slack import parser
from omnibot.services.slack.base_message import BaseMessage
from omnibot.services.slack.bot import Bot

logger = logging.getLogger(__name__)


class Message(BaseMessage):
    """
    Class for representing a parsed slack message.
    """

    def __init__(self, bot: Bot, event: dict, event_trace: dict):
        super().__init__(bot, event, event_trace, "message")
        self._payload["ts"] = event["ts"]
        self._payload["thread_ts"] = event.get("thread_ts")
        self._payload["parent_user_id"] = event.get("parent_user_id")
        self._check_unsupported()
        try:
            self._payload["text"] = event["text"]
        except Exception:
            logger.error(
                "Message event is missing text attribute.",
                extra=self.event_trace,
            )
            raise
        self._payload["parsed_text"] = self.text
        self._payload["channel_id"] = event["channel"]
        self._event_trace["channel_id"] = self.channel_id
        self._payload["channel"] = slack.get_channel(self.bot, self.channel_id)
        if not self.channel:
            logger.error(
                "Failed to fetch channel from channel_id.",
                extra=self.event_trace,
            )

        self._parse_payload()

    def _check_unsupported(self):
        # TODO: make the ignores configurable, but have a default list
        # Ignore self
        # Ignore bots
        unsupported = False
        if self.bot_id:
            logger.debug("ignoring message from bot", extra=self.event_trace)
            unsupported = True
        # Ignore slackbot as it doesn't get classifed as a bot user
        elif self.user and self.user == "USLACKBOT":
            logger.debug("ignoring message from slackbot", extra=self.event_trace)
            unsupported = True
        # For now, ignore all event subtypes
        elif self.subtype:
            extra = {"subtype": self.subtype}
            extra.update(self.event_trace)
            logger.debug(
                "ignoring message with unsupported subtype",
                extra=extra,
            )
            unsupported = True
        if unsupported:
            statsd = stats.get_statsd_client()
            statsd.incr("event.unsupported")
            raise MessageUnsupportedError()

    def _parse_payload(self):
        try:
            self._payload["users"] = parser.extract_users(self.text, self.bot)
            self._payload["parsed_text"] = parser.replace_users(
                self.parsed_text,
                self.users,
            )
        except Exception:
            logger.exception(
                "Failed to extract user info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["channels"] = parser.extract_channels(self.text, self.bot)
            self._payload["parsed_text"] = parser.replace_channels(
                self.parsed_text,
                self.channels,
            )
        except Exception:
            logger.exception(
                "Failed to extract channel info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["subteams"] = parser.extract_subteams(self.text, self.bot)
        except Exception:
            logger.exception(
                "Failed to extract subteam info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["specials"] = parser.extract_specials(self.text)
            self._payload["parsed_text"] = parser.replace_specials(
                self.parsed_text,
                self.specials,
            )
        except Exception:
            logger.exception(
                "Failed to extract special info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["emojis"] = parser.extract_emojis(self.text)
        except Exception:
            logger.exception(
                "Failed to extract emoji info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["emails"] = parser.extract_emails(self.text)
            self._payload["parsed_text"] = parser.replace_emails(
                self.parsed_text,
                self.emails,
            )
        except Exception:
            logger.exception(
                "Failed to extract email info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["urls"] = parser.extract_urls(self.text)
            self._payload["parsed_text"] = parser.replace_urls(
                self.parsed_text,
                self.urls,
            )
        except Exception:
            logger.exception(
                "Failed to extract url info from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        try:
            self._payload["directed"] = parser.extract_mentions(
                # We match mentioned and directed against parsed users, not
                # against raw users.
                self.parsed_text,
                self.bot,
                self.channel,
            )
        except Exception:
            logger.exception(
                "Failed to extract mentions from text.",
                exc_info=True,
                extra=self.event_trace,
            )
        self._payload["mentioned"] = False
        for user_id, user_name in self.users.items():
            if self.bot.name == user_name:
                self._payload["mentioned"] = True
            if f"<@{self.bot.user_id}>" == user_id:
                self._payload["mentioned"] = True
        try:
            self._payload["command_text"] = parser.extract_command(
                # Similar to mentions above, we find the command text
                # from pre-parsed text for users, not against raw users.
                self.parsed_text,
                self.bot,
            )
        except Exception:
            logger.exception(
                "Failed to extract command_text from text.",
                exc_info=True,
                extra=self.event_trace,
            )

    @property
    def subtype(self):
        return self.event.get("subtype")

    @property
    def text(self):
        return self._payload["text"]

    @property
    def parsed_text(self):
        return self._payload["parsed_text"]

    @property
    def directed(self):
        return self._payload.get("directed", False)

    @property
    def mentioned(self):
        return self._payload.get("mentioned", False)

    @property
    def thread_ts(self):
        """
        The timestamp of the parent message, if this is a reply to a message.
        :return:
        """
        return self._payload["thread_ts"]

    @property
    def parent_user_id(self):
        """
        The user_id of the parent message, if this is a reply to a message.
        """
        return self._payload["parent_user_id"]

    @property
    def channels(self):
        return self._payload.get("channels", {})

    @property
    def users(self):
        return self._payload.get("users", {})

    @property
    def specials(self):
        return self._payload.get("specials", {})

    @property
    def emails(self):
        return self._payload.get("emails", {})

    @property
    def urls(self):
        return self._payload.get("urls", {})


class MessageUnsupportedError(Exception):
    pass
