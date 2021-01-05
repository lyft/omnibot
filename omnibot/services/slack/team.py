from omnibot import settings


class Team(object):
    """
    Class for representing a slack team.
    """

    def __init__(self, name, team_id):
        self._name = name
        self._team_id = team_id

    def __eq__(self, other):
        if not isinstance(other, Team):
            return False
        return self._name == other._name and self._team_id == other._team_id

    def __hash__(self):
        return hash((self._name, self._team_id))

    @classmethod
    def get_team_by_name(cls, name):
        team_id = settings.SLACK_TEAMS.get(name)
        if not team_id:
            raise TeamInitializationError('Invalid team')
        return cls(name, team_id)

    @classmethod
    def get_team_by_id(cls, team_id):
        name = None
        for team_name, _team_id in settings.SLACK_TEAMS.items():
            if _team_id == team_id:
                name = team_name
                break
        if not name:
            raise TeamInitializationError('Invalid team')
        return cls(name, team_id)

    @property
    def name(self):
        return self._name

    @property
    def team_id(self):
        return self._team_id

    @property
    def logging_context(self):
        return {
            'team': self.name,
            'team_id': self.team_id,
        }


class TeamInitializationError(Exception):
    pass
