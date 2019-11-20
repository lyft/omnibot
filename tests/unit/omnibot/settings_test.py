from omnibot import settings


def test_primary_slack_bot():
    assert settings.PRIMARY_SLACK_BOT['testteam'] == 'testteambot'
    assert settings.PRIMARY_SLACK_BOT['test2ndteam'] == 'test2ndteambot'


def test_slack_teams():
    assert settings.SLACK_TEAMS['testteam'] == 'T12345678'
    assert settings.SLACK_TEAMS['test2ndteam'] == 'TABCDEF12'


def test_slack_bot_tokens():
    assert 'testteam' in settings.SLACK_BOT_TOKENS
    assert 'test2ndteam' in settings.SLACK_BOT_TOKENS
    required_keys = [
        'verification_token',
        'oauth_token',
        'oauth_bot_token',
        'app_id'
    ]
    assert 'echobot' in settings.SLACK_BOT_TOKENS['testteam']
    for key in required_keys:
        assert key in settings.SLACK_BOT_TOKENS['testteam']['echobot']
    assert 'pingbot' in settings.SLACK_BOT_TOKENS['testteam']
    assert 'commandbot' in settings.SLACK_BOT_TOKENS['testteam']
    assert 'mentionbot' in settings.SLACK_BOT_TOKENS['testteam']
    # missing oauth bot token, but has oauth token
    assert 'echobot' in settings.SLACK_BOT_TOKENS['test2ndteam']
    for key in required_keys:
        assert key in settings.SLACK_BOT_TOKENS['test2ndteam']['echobot']
    assert settings.SLACK_BOT_TOKENS['test2ndteam']['echobot']['oauth_token'] != ''
    assert settings.SLACK_BOT_TOKENS['test2ndteam']['echobot']['oauth_bot_token'] == ''
    # missing verification token
    assert 'pingbot' not in settings.SLACK_BOT_TOKENS['test2ndteam']
    # missing oauth tokens
    assert 'channelchannelbot' not in settings.SLACK_BOT_TOKENS['test2ndteam']


def test_handlers():
    assert 'slash_command_handlers' in settings.HANDLERS
    assert 'message_handlers' in settings.HANDLERS
