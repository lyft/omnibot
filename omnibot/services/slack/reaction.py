from omnibot import logging
from omnibot.services import slack
from omnibot.services import stats

logger = logging.getLogger(__name__)


class Reaction:
    """
    Class for representing a parsed slack reaction.
    """

    def __init__(self, bot, event, event_trace):
        self._event_trace = event_trace
        self.event = event
        self._match = None
        self._payload = {}
        self._payload["omnibot_payload_type"] = "reaction"
        self._bot = bot
        # The bot object has data we don't want to pass to downstreams, so
        # in the payload, we just store specific bot data.
        self._payload["bot"] = {"name": bot.name, "bot_id": bot.bot_id}
        # For future safety sake, we'll do the same for the team.
        self._payload["team"] = {"name": bot.team.name, "team_id": bot.team.team_id}
        self._payload["ts"] = event["event_ts"]
        self._payload["user"] = event.get("user")
        self._check_unsupported()
        if self.user:
            self._payload["parsed_user"] = slack.get_user(self.bot, self.user)
        elif self.bot_id:
            # TODO: call get_bot
            self._payload["parsed_user"] = None
        else:
            self._payload["parsed_user"] = None
        self._payload["type"] = event["type"]
        try:
            self._payload["reaction"] = event["reaction"]
        except Exception:
            logger.error(
                "Reaction event is missing reaction attribute.",
                extra=self.event_trace,
            )
            raise
        try:
            self._payload["reaction"] = event["reaction"]
        except Exception:
            logger.error(
                "Reaction event is missing reaction attribute.",
                extra=self.event_trace,
            )
            raise
        try:
            self._payload["item_type"] = event["item"]["type"]
            self._payload["item_channel"] = event["item"]["channel"]
            self._payload["item_ts"] = event["item"]["ts"]
        except Exception:
            logger.error(
                "Reaction event is missing a item attribute.",
                extra=self.event_trace,
            )
            raise
        self._payload["channel_id"] = event["item"]["channel"]
        self._event_trace["channel_id"] = self.channel_id
        self._payload["channel"] = slack.get_channel(self.bot, self.channel_id)
        if not self.channel:
            logger.error(
                "Failed to fetch channel from channel_id.",
                extra=self.event_trace,
            )

    def _check_unsupported(self):
        # TODO: make the ignores configurable, but have a default list
        # Ignore self
        # Ignore bots
        unsupported = False
        if self.bot_id:
            logger.debug("ignoring reaction from bot", extra=self.event_trace)
            unsupported = True
        # Ignore slackbot as it doesn't get classified as a bot user
        elif self.user and self.user == "USLACKBOT":
            logger.debug("ignoring reaction from slackbot", extra=self.event_trace)
            unsupported = True
        if unsupported:
            statsd = stats.get_statsd_client()
            statsd.incr("event.unsupported")
            raise ReactionUnsupportedError()

    @property
    def channel_id(self):
        return self._payload.get("channel_id")

    @property
    def channel(self):
        return self._payload.get("channel", {})

    @property
    def user(self):
        return self._payload["user"]

    @property
    def ts(self):
        return self._payload["ts"]

    @property
    def bot(self):
        """
        The bot associated with the app that received this reaction from the
        event subscription api. To get info about a bot that may have sent
        this reaction, see bot_id.
        """
        return self._bot

    @property
    def bot_id(self):
        """
        The bot_id associated with the reaction, if the reaction is from a bot.
        If this reaction isn't from a bot, this will return None.
        """
        return self.event.get("bot_id")

    @property
    def payload(self):
        return self._payload

    @property
    def event_trace(self):
        return self._event_trace

    @property
    def item_type(self):
        return self._payload["item_type"]

    @property
    def item_channel(self):
        return self._payload["item_channel"]

    @property
    def item_ts(self):
        return self._payload["item_ts"]


class ReactionUnsupportedError(Exception):
    pass
