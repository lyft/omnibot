from omnibot import logging
from omnibot.services import stats
from omnibot.services.slack.base_message import BaseMessage
from omnibot.services.slack.bot import Bot

logger = logging.getLogger(__name__)


class Reaction(BaseMessage):
    """
    Class for representing a parsed slack reaction.
    """

    def __init__(self, bot: Bot, event: dict, event_trace: dict):
        # `bot` is the receiving bot instance handling this reaction event,
        # not the user or bot who sent the reaction.
        super().__init__(bot, event, event_trace, "reaction")
        self._payload["ts"] = event["event_ts"]
        self._check_unsupported()
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
        self._payload["channel_id"] = self.item_channel

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
    def item_type(self):
        """
        The type of the item (e.g. "message", "file", etc.) that was reacted to.
        """
        return self._payload["item_type"]

    @property
    def item_channel(self):
        """
        The channel the (e.g. "message", "file", etc.) that was reacted to was in.
        """
        return self._payload["item_channel"]

    @property
    def item_ts(self):
        """
        The timestamp of the item (e.g. "message", "file", etc.) that was reacted to.
        """
        return self._payload["item_ts"]

    @property
    def reaction(self):
        """
        The emoji name of the reaction (e.g. "+1", "-1", "smile", etc.).
        """
        return self._payload["reaction"]


class ReactionUnsupportedError(Exception):
    pass
