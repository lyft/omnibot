import pytest

from omnibot.services.slack.team import Team
from omnibot.services.slack.team import TeamInitializationError


def test_team():
    _team = Team.get_team_by_name("testteam")
    assert _team.name == "testteam"
    assert _team.team_id == "T12345678"

    _team = Team.get_team_by_id("TABCDEF12")
    assert _team.name == "test2ndteam"
    assert _team.team_id == "TABCDEF12"

    with pytest.raises(TeamInitializationError):
        _team = Team.get_team_by_name("faketeam")

    with pytest.raises(TeamInitializationError):
        _team = Team.get_team_by_id(team_id="BADTEAMID")
