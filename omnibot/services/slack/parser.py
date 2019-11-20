import re

from omnibot.services import slack
from omnibot.services import stats


def extract_users(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_users'):
        # Example: <@U024BE7LH> or <@U024BE7LH|bob-marley> or <@W024BE7LH|bob-marley>
        user_arr = {}
        users = re.findall('<@[UW]\w+(?:\|[\w-]+)?>', text)
        for user in users:
            match = re.match('<@([UW]\w+)(\|[\w-]+)?>', user)
            user_name = None
            if match.group(2) is not None:
                # user name is embedded; use the second match and strip |
                user_name = match.group(2)[1:]
            else:
                user_id = match.group(1)
                user_data = slack.get_user(bot, user_id)
                if user_data:
                    user_name = user_data['name']
            user_arr[user] = user_name
        return user_arr


def replace_users(text, users):
    for user, user_name in users.items():
        if user_name is not None:
            text = text.replace(
                user,
                '@{}'.format(user_name)
            )
    return text


def extract_channels(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_channels'):
        # Example: <#C024BE7LR> or <#C024BE7LR|general-room>
        channel_arr = {}
        channels = re.findall('<#C\w+(?:\|[\w-]+)?>', text)
        for channel in channels:
            match = re.match('<#(C\w+)(\|[\w-]+)?>', channel)
            channel_name = None
            if match.group(2) is not None:
                # channel name is embedded; use the second match and strip |
                channel_name = match.group(2)[1:]
            else:
                channel_id = match.group(1)
                channel_data = slack.get_channel(bot, channel_id)
                if not channel_data:
                    continue
                channel_name = channel_data['name']
            channel_arr[channel] = channel_name
        return channel_arr


def replace_channels(text, channels):
    for channel, channel_name in channels.items():
        if channel_name is not None:
            text = text.replace(
                channel,
                '#{}'.format(channel_name)
            )
    return text


def extract_subteams(text, bot):
    statsd = stats.get_statsd_client()
    # TODO: parse this
    with statsd.timer('parser.extract_subteams'):
        # Example: <!subteam^S012345|happy-peeps>
        # subteams = re.findall(
        #     '<!subteam\^S\w+(?:\|@[\w-]+)?>',
        #     metadata['text']
        # )
        subteam_arr = {}
        # for subteam in subteams:
        #     metadata['subteams'][subteam] = None
        return subteam_arr


def extract_specials(text):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_specials'):
        # Example: <!here|@here>
        specials = re.findall('<!\w+(?:\|@[\w-]+)?>', text)
        special_arr = {}
        for special in specials:
            match = re.match('<!(\w+)(?:\|@[\w-]+)?>', special)
            special_label = None
            if match.group(1) is not None:
                special_label = '@{}'.format(match.group(1))
            special_arr[special] = special_label
        return special_arr


def replace_specials(text, specials):
    for special, special_label in specials.items():
        if special_label is not None:
            text = text.replace(
                special,
                special_label
            )
    return text


def extract_emojis(text):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_emojis'):
        # Example: :test_me: or :test-me:
        emojis = re.findall(':[a-z0-9_\+\-]+:', text)
        emoji_arr = {}
        for emoji in emojis:
            match = re.match(':([a-z0-9_\+\-]+):', emoji)
            emoji_name = None
            if match.group(1) is not None:
                emoji_name = match.group(1)
            emoji_arr[emoji] = emoji_name
        return emoji_arr


def extract_emails(text):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_emails'):
        # Example: <mailto:example@example.com|example@example.com>
        emails = re.findall(
            # [^>]* is non-greedy .*
            '<mailto:([^>]*)(?:\|[^>]*)?>',
            text
        )
        email_arr = {}
        for email in emails:
            unparsed_email = '<mailto:{0}>'.format(email)
            email_label = email.split('|')[0]
            email_arr[unparsed_email] = email_label
        return email_arr


def replace_emails(text, emails):
    for email, email_label in emails.items():
        if email_label is not None:
            text = text.replace(
                email,
                email_label
            )
    return text


def extract_urls(text):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_urls'):
        # Example: <http://test.com> or <http://test.com|test.com>
        # [^>]* is non-greedy .*
        urls = re.findall('<(http[s]?://[^>]*)(?:\|[^>]*)?>', text)
        url_arr = {}
        for url in urls:
            unparsed_url = '<{0}>'.format(url)
            url_label = url.split('|')[0]
            url_arr[unparsed_url] = url_label
        return url_arr


def replace_urls(text, urls):
    for url, url_label in urls.items():
        if url_label is not None:
            text = text.replace(
                url,
                url_label
            )
    return text


def extract_mentions(text, bot, channel):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_mentions'):
        to_me = False
        at_me = '@{}'.format(bot.name)
        if text.split(' ')[0] == at_me:
            to_me = True
        directed = channel.get('is_im') or to_me
        return directed


def extract_command(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.extract_command'):
        at_me = '@{}'.format(bot.name)
        if text.startswith(at_me):
            command_text = text[len(at_me):].strip()
        elif at_me in text:
            command_text = re.sub(
                r'.*{}'.format(at_me),
                '',
                text
            ).strip()
        else:
            command_text = text
        return command_text


def unextract_specials(text):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.unextract_specials'):
        # Example: @here
        specials = re.findall('(@here|@channel)', text)
        for special in specials:
            text = text.replace(
                special,
                '<!{0}|{0}>'.format(special[1:])
            )
        return text


def unextract_channels(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.unextract_channels'):
        # Example: #my-channel
        _channel_labels = re.findall('(^#[\w\-_]+| #[\w\-_]+)', text)
        for label in _channel_labels:
            channel = slack.get_channel_by_name(bot, label.strip())
            if not channel:
                continue
            text = text.replace(
                '#{}'.format(channel['name']),
                '<#{0}|{1}>'.format(
                    channel['id'],
                    channel['name']
                )
            )
        return text


def unextract_users(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer('parser.unextract_users'):
        # Example: @my-user
        _user_labels = re.findall('(^@[\w\-_]+| @[\w\-_]+)', text)
        user_labels = []
        for label in _user_labels:
            user_labels.append(label.strip())
        for label in user_labels:
            user = slack.get_user_by_name(bot, label)
            if not user:
                continue
            text = text.replace(
                label,
                '<@{0}|{1}>'.format(
                    user['id'],
                    slack.get_name_from_user(user)
                )
            )
        return text
