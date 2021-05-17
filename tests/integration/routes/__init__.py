from omnibot.services.slack.bot import Bot
from omnibot.services.slack.team import Team


class BotMatcher:
    expected: Bot

    def __init__(self, expected: Bot):
        self.expected = expected

    def __eq__(self, other: Bot):
        return (
            self.expected.bot_id == other.bot_id
            and self.expected.name == other.name
            and self.expected.team.name == other.team.name
            and self.expected.team.team_id == other.team.team_id
        )


def get_test_bot() -> BotMatcher:
    return BotMatcher(
        Bot.get_bot_by_bot_id(Team.get_team_by_id("TEST_TEAM_ID"), "TEST_OMNIBOT_ID")
    )
