import re

from omnibot.services import slack
from omnibot.services import stats

SPACE_REGEX = re.compile(r"[\s\u00A0]")


def extract_users(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_users"):
        # Example: <@U024BE7LH> or <@U024BE7LH|bob-marley> or <@W024BE7LH|bob-marley>
        user_arr = {}
        users = re.findall(r"<@[UW]\w+(?:\|[\w-]+)?>", text)
        for user in users:
            match = re.match(r"<@([UW]\w+)(\|[\w-]+)?>", user)
            user_name = None
            if match.group(2) is not None:
                # user name is embedded; use the second match and strip |
                user_name = match.group(2)[1:]
            else:
                user_id = match.group(1)
                user_data = slack.get_user(bot, user_id)
                if user_data:
                    user_name = user_data["name"]
            user_arr[user] = user_name
        return user_arr


def replace_users(text, users):
    for user, user_name in users.items():
        if user_name is not None:
            text = text.replace(user, f"@{user_name}")
    return text


def extract_channels(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_channels"):
        # Example: <#C024BE7LR> or <#C024BE7LR|general-room>
        channel_arr = {}
        channels = re.findall(r"<#C\w+(?:\|[\w-]+)?>", text)
        for channel in channels:
            match = re.match(r"<#(C\w+)(\|[\w-]+)?>", channel)
            channel_name = None
            if match.group(2) is not None:
                # channel name is embedded; use the second match and strip |
                channel_name = match.group(2)[1:]
            else:
                channel_id = match.group(1)
                channel_data = slack.get_channel(bot, channel_id)
                if not channel_data:
                    continue
                channel_name = channel_data["name"]
            channel_arr[channel] = channel_name
        return channel_arr


def replace_channels(text, channels):
    for channel, channel_name in channels.items():
        if channel_name is not None:
            text = text.replace(channel, f"#{channel_name}")
    return text


def extract_subteams(text, bot):
    statsd = stats.get_statsd_client()
    # TODO: parse this
    with statsd.timer("parser.extract_subteams"):
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
    with statsd.timer("parser.extract_specials"):
        # Example: <!here|@here>
        specials = re.findall(r"<!\w+(?:\|@[\w-]+)?>", text)
        special_arr = {}
        for special in specials:
            match = re.match(r"<!(\w+)(?:\|@[\w-]+)?>", special)
            special_label = None
            if match.group(1) is not None:
                special_label = f"@{match.group(1)}"
            special_arr[special] = special_label
        return special_arr


def replace_specials(text, specials):
    for special, special_label in specials.items():
        if special_label is not None:
            text = text.replace(special, special_label)
    return text


def extract_emojis(text):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_emojis"):
        # Example: :test_me: or :test-me:
        emojis = re.findall(r":[a-z0-9_\+\-]+:", text)
        emoji_arr = {}
        for emoji in emojis:
            match = re.match(r":([a-z0-9_\+\-]+):", emoji)
            emoji_name = None
            if match.group(1) is not None:
                emoji_name = match.group(1)
            emoji_arr[emoji] = emoji_name
        return emoji_arr


def extract_emails(text):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_emails"):
        # Example: <mailto:example@example.com|example@example.com>
        emails = re.findall(
            # [^>]* is non-greedy .*
            r"<mailto:([^>]*)(?:\|[^>]*)?>",
            text,
        )
        email_arr = {}
        for email in emails:
            unparsed_email = f"<mailto:{email}>"
            email_label = email.split("|")[0]
            email_arr[unparsed_email] = email_label
        return email_arr


def replace_emails(text, emails):
    for email, email_label in emails.items():
        if email_label is not None:
            text = text.replace(email, email_label)
    return text


def extract_urls(text):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_urls"):
        # Example: <http://test.com> or <http://test.com|test.com>
        # [^>]* is non-greedy .*
        urls = re.findall(r"<(http[s]?://[^>]*)(?:\|[^>]*)?>", text)
        url_arr = {}
        for url in urls:
            unparsed_url = f"<{url}>"
            url_label = url.split("|")[0]
            url_arr[unparsed_url] = url_label
        return url_arr


def replace_urls(text, urls):
    for url, url_label in urls.items():
        if url_label is not None:
            text = text.replace(url, url_label)
    return text


def extract_mentions(text, bot, channel):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_mentions"):
        to_me = False
        at_me = f"@{bot.name}"
        if SPACE_REGEX.split(text)[0] == at_me:
            to_me = True
        directed = channel.get("is_im") or to_me
        return directed


def extract_command(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.extract_command"):
        at_me = f"@{bot.name}"
        if text.startswith(at_me):
            command_text = text[len(at_me) :].strip()  # noqa:E203
        elif at_me in text:
            command_text = re.sub(rf".*{at_me}", "", text).strip()
        else:
            command_text = text
        return command_text


def unextract_specials(text):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.unextract_specials"):
        # Example: @here
        specials = re.findall("(@here|@channel)", text)
        for special in specials:
            text = text.replace(special, "<!{0}|{0}>".format(special[1:]))
        return text


def unextract_channels(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.unextract_channels"):
        # Example: #my-channel
        _channel_labels = re.findall(r"(^#[\w\-_]+| #[\w\-_]+)", text)
        for label in _channel_labels:
            channel = slack.get_channel_by_name(bot, label.strip())
            if not channel:
                continue
            text = text.replace(
                "#{}".format(channel["name"]),
                "<#{}|{}>".format(channel["id"], channel["name"]),
            )
        return text


def unextract_users(text, bot):
    statsd = stats.get_statsd_client()
    with statsd.timer("parser.unextract_users"):
        # Example: @my-user
        _user_labels = re.findall(r"(^@[\w\-_]+| @[\w\-_]+)", text)
        user_labels = []
        for label in _user_labels:
            user_labels.append(label.strip())
        for label in user_labels:
            user = slack.get_user_by_name(bot, label)
            if not user:
                continue
            text = text.replace(
                label,
                "<@{}|{}>".format(user["id"], slack.get_name_from_user(user)),
            )
        return text
