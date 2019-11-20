from omnibot import settings
from omnibot.services.slack.team import Team


class Bot(object):
    """
    Class for representing a slack bot.
    """

    def __init__(self, team, name, data):
        self._team = team
        self._name = name
        self._bot_data = data
        self._interactive_component_handlers = []
        self._slash_command_handlers = []
        self._message_handlers = []
        self._configure_handlers()

    def _configure_handlers(self):
        handlers = settings.HANDLERS
        for handler in handlers.get('interactive_component_handlers', []):
            bots = handler.get('bots', {}).get(self.team.name, {})
            if self.name in bots:
                self._interactive_component_handlers.append(handler)
        for handler in handlers.get('slash_command_handlers', []):
            bots = handler.get('bots', {}).get(self.team.name, {})
            if self.name in bots:
                self._slash_command_handlers.append(handler)
        for handler in handlers.get('message_handlers', []):
            bots = handler.get('bots', {}).get(self.team.name, {})
            if self.name in bots:
                self._message_handlers.append(handler)

    @classmethod
    def get_bot_by_name(cls, team, name):
        bots = settings.SLACK_BOT_TOKENS.get(team.name, {})
        _bot_data = bots.get(name, {})
        if not _bot_data:
            raise BotInitializationError('Invalid bot')
        return cls(team, name, _bot_data)

    @classmethod
    def get_bot_by_bot_id(cls, team, bot_id):
        name = None
        _bot_data = {}
        bots = settings.SLACK_BOT_TOKENS.get(team.name, {})
        for bot_name, bot_data in bots.items():
            if bot_id == bot_data.get('app_id'):
                name = bot_name
                _bot_data = bot_data
                break
        if not _bot_data:
            raise BotInitializationError('Invalid bot')
        return cls(team, name, _bot_data)

    @classmethod
    def get_bot_by_verification_token(cls, verification_token):
        name = None
        _bot_data = {}
        for team_name, bots in settings.SLACK_BOT_TOKENS.items():
            for bot_name, bot_data in bots.items():
                if verification_token == bot_data['verification_token']:
                    name = bot_name
                    _bot_data = bot_data
                    break
        if not _bot_data:
            raise BotInitializationError('Invalid bot')
        team = Team.get_team_by_name(team_name)
        return cls(team, name, _bot_data)

    @property
    def team(self):
        return self._team

    @property
    def name(self):
        return self._name

    @property
    def bot_id(self):
        return self._bot_data.get('app_id')

    @property
    def verification_token(self):
        try:
            return self._bot_data.get('verification_token')
        except KeyError:
            return None

    @property
    def oauth_token(self):
        try:
            return self._bot_data.get('oauth_token')
        except KeyError:
            return None

    @property
    def oauth_bot_token(self):
        try:
            return self._bot_data.get('oauth_bot_token')
        except KeyError:
            return None

    @property
    def interactive_component_handlers(self):
        return self._interactive_component_handlers

    @property
    def slash_command_handlers(self):
        return self._slash_command_handlers

    @property
    def message_handlers(self):
        return self._message_handlers


class BotInitializationError(Exception):
    pass
