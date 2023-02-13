from omnibot.services.slack.parser import extract_users, extract_mentions


def test_extract_user():
    assert extract_users("<@W024BE7LH|logan-smith>", "ball") == {
        "<@W024BE7LH|logan-smith>": "logan-smith"
    }
    assert extract_users("<@U024BE7LH|logan-smith>", "ball") == {
        "<@U024BE7LH|logan-smith>": "logan-smith"
    }


# we do not support G so nothing should be returned
def test_not_supported_extract():
    assert extract_users("<@G024BE7LH|logan-smith>", "ball") == {}


def test_extract_mentions(mocker):
    mock_bot = mocker.patch("omnibot.services.slack.bot.Bot")
    mock_bot.return_value.name = "omnibot"
    assert extract_mentions("@omnibot testcommand", mock_bot.return_value, {})
    assert extract_mentions("@omnibot\u00A0testcommand", mock_bot.return_value, {})
    assert not extract_mentions("@omnibottestcommand", mock_bot.return_value, {})
