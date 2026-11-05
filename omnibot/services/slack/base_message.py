from omnibot import logging
from omnibot.services import slack
from omnibot.services.slack.bot import Bot

logger = logging.getLogger(__name__)


class BaseMessage:
    """
    Base class for representing a parsed slack event message.
    """

    def __init__(
        self,
        bot: Bot,
        event: dict,
        event_trace: dict,
        omnibot_payload_type: str,
    ):
        self._event_trace = event_trace
        self.event = event
        self._match = None
        self._payload = {}
        self._payload["omnibot_payload_type"] = omnibot_payload_type
        self._payload["event_type"] = event.get("type")
        self._bot = bot
        # The bot object has data we don't want to pass to downstreams, so
        # in the payload, we just store specific bot data.
        self._payload["bot"] = {"name": bot.name, "bot_id": bot.bot_id}
        # For future safety sake, we'll do the same for the team.
        self._payload["team"] = {"name": bot.team.name, "team_id": bot.team.team_id}
        self._payload["user"] = event.get("user")
        if self.user:
            self._payload["parsed_user"] = slack.get_user(self.bot, self.user)
        elif self.bot_id:
            # TODO: call get_bot
            self._payload["parsed_user"] = None
        else:
            self._payload["parsed_user"] = None

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
        return self.event.get("bot_id")

    @property
    def event_trace(self):
        return self._event_trace

    @property
    def team(self):
        return self._payload["team"]

    @property
    def payload(self):
        return self._payload

    @property
    def user(self):
        return self._payload["user"]

    @property
    def channel_id(self):
        return self._payload.get("channel_id")

    @property
    def channel(self):
        return self._payload.get("channel", {})

    @property
    def ts(self):
        """
        The timestamp of the event.
        """
        return self._payload["ts"]

    @property
    def match_type(self):
        return self._payload.get("match_type")

    @property
    def match(self):
        return self._match

    @property
    def command_text(self):
        return self._payload.get("command_text")

    @property
    def args(self):
        """
        Used during callback for omnibot receiver route rule matching.
        """
        return self._payload.get("args")

    def set_match(self, match_type: str, match: str):
        self._payload["match_type"] = match_type
        self._match = match
        if match_type == "command":
            self._payload["command"] = match
            self._payload["args"] = self.command_text[len(match):].strip()  # fmt: skip
        elif match_type == "regex":
            self._payload["regex"] = match
        elif match_type == "reaction":
            self._payload["reaction"] = match
            self._payload["args"] = self._payload.get("emoji_name")
