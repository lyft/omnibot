"""
Slackclient wrapper.
"""
import json

import gevent
import slackclient

from omnibot import logging
from omnibot.services import omniredis
from omnibot.utils import merge_logging_context

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
GEVENT_SLEEP_TIME = 5

# TODO: locking for long-running updates
_client = {}


def client(bot, client_type="bot"):
    """
    Global Slack client.
    """
    global _client
    team_name = bot.team.name
    if team_name not in _client:
        _client[team_name] = {}
    if bot.name not in _client[team_name]:
        _client[team_name][bot.name] = {}
        if bot.oauth_bot_token:
            _client[team_name][bot.name]["bot"] = slackclient.SlackClient(
                bot.oauth_bot_token,
            )
        if bot.oauth_user_token:
            _client[team_name][bot.name]["user"] = slackclient.SlackClient(
                bot.oauth_user_token,
            )
    if client_type == "bot":
        try:
            return _client[team_name][bot.name]["bot"]
        except KeyError:
            pass
    elif client_type == "user":
        return _client[team_name][bot.name]["user"]


def _get_failure_context(result):
    """
    Get the logging context from a failed slack call.
    """
    ret = {}
    for attr in ["error", "needed", "provided"]:
        if attr in result:
            ret[attr] = result[attr]
    return ret


def _get_conversations(bot, team):
    """
    Get all conversations
    """
    conversations = []
    retry = 0
    next_cursor = ""
    while True:
        conversations_data = client(bot).api_call(
            "conversations.list",
            exclude_archived=True,
            exclude_members=True,
            limit=1000,
            cursor=next_cursor,
            team_id=team.team_id,
        )
        if conversations_data["ok"]:
            conversations.extend(conversations_data["channels"])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error(
                    "Exceeded max retries when calling conversations.list.",
                    extra=bot.logging_context,
                )
                break
            logger.warning(
                "Call to channels.list failed, attempting retry",
                extra=merge_logging_context(
                    {"retry": retry},
                    _get_failure_context(conversations_data),
                    bot.logging_context,
                ),
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
        next_cursor = conversations_data.get("response_metadata", {}).get("next_cursor")
        if not next_cursor:
            break
        gevent.sleep(GEVENT_SLEEP_TIME)
    return conversations


def update_conversations(bot, team):
    for conversation in _get_conversations(bot, team):
        if conversation.get("is_channel", False):
            update_channel(bot, conversation)
        elif conversation.get("is_group", False):
            update_group(bot, conversation)
        elif conversation.get("is_im", False):
            update_im(bot, conversation)
        elif conversation.get("is_mpim", False):
            update_mpim(bot, conversation)
        else:
            logger.info(
                "Not updating unsupported conversation.",
                extra=merge_logging_context(
                    bot.logging_context,
                    {"channel": conversation["id"]},
                ),
            )


def update_channel(bot, channel):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(
        f"channels:{bot.team.name}",
        channel["id"],
        json.dumps(channel),
    )
    redis_client.hset(
        f"channelsmap:{bot.team.name}",
        channel["name"],
        channel["id"],
    )


def get_channels(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter(f"channels:{bot.team.name}")


def update_group(bot, group):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(f"groups:{bot.team.name}", group["id"], json.dumps(group))
    redis_client.hset(
        f"groupsmap:{bot.team.name}",
        group["name"],
        group["id"],
    )


def get_groups(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter(f"groups:{bot.team.name}")


def update_im(bot, im):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(f"ims:{bot.team.name}", im["id"], json.dumps(im))
    redis_client.hset(
        f"imsmap:{bot.team.name}",
        im["user"],
        im["id"],
    )


def get_ims(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter(f"ims:{bot.team.name}")


def get_im_channel_id(bot, user_id):
    redis_client = omniredis.get_redis_client()
    imsmap_id = redis_client.hget(f"imsmap:{bot.team.name}", user_id)
    if imsmap_id:
        raw_im = redis_client.hget(f"ims:{bot.team.name}", imsmap_id)
        if raw_im:
            im = json.loads(raw_im)
            if not im.get("is_user_deleted", False):
                return im["id"]

    retry = 0
    while True:
        users = user_id
        conversation_data = client(bot).api_call("conversations.open", users=users)
        if conversation_data["ok"]:
            return conversation_data["channel"]["id"]
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error(
                    "Exceeded max retries when calling conversations.open.",
                    extra=bot.logging_context,
                )
                break
            logger.warning(
                "Call to conversations.open failed, attempting retry",
                extra=merge_logging_context(
                    {"retry": retry},
                    _get_failure_context(conversation_data),
                    bot.logging_context,
                ),
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
    return None


def update_mpim(bot, mpim):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(f"mpims:{bot.team.name}", mpim["id"], json.dumps(mpim))
    redis_client.hset(
        f"mpimsmap:{bot.team.name}",
        mpim["name"],
        mpim["id"],
    )


def get_mpims(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter(f"mpims:{bot.team.name}")


def _get_emoji(bot):
    # TODO: split this retry logic into a generic retry function
    for retry in range(MAX_RETRIES):
        resp = client(bot).api_call("emoji.list")
        if resp["ok"]:
            break
        logger.warning(
            "Call to emoji.list failed, attempting retry",
            extra=merge_logging_context(
                {"retry": retry},
                _get_failure_context(resp),
                bot.logging_context,
            ),
        )
        gevent.sleep(GEVENT_SLEEP_TIME)
    else:
        logger.error(
            "Exceeded max retries when calling emoji.list.",
            extra=bot.logging_context,
        )
        return {}

    emoji = {}
    for k, v in resp["emoji"].items():
        while v.startswith("alias:"):
            _, _, alias = v.partition(":")
            v = resp["emoji"].get(alias, "")
        if v:
            emoji[k] = v
    return emoji


def update_emoji(bot):
    redis_client = omniredis.get_redis_client()
    for k, v in _get_emoji(bot).items():
        redis_client.hset(f"emoji:{bot.team.name}", k, v)


def get_emoji(bot, name):
    redis_client = omniredis.get_redis_client()
    return redis_client.hget(f"emoji:{bot.team.name}", name)


def _get_channel_from_cache(bot, channel):
    redis_client = omniredis.get_redis_client()
    channel_data = redis_client.hget(f"channels:{bot.team.name}", channel)
    if channel_data:
        return json.loads(channel_data)
    group_data = redis_client.hget(f"groups:{bot.team.name}", channel)
    if group_data:
        return json.loads(group_data)
    im_data = redis_client.hget(f"ims:{bot.team.name}", channel)
    if im_data:
        return json.loads(im_data)
    mpim_data = redis_client.hget(f"mpims:{bot.team.name}", channel)
    if mpim_data:
        return json.loads(mpim_data)
    return None


def get_channel(bot, channel):
    """
    Get a channel, from its channel id
    """
    logger.debug(
        "Fetching channel",
        extra=merge_logging_context(
            {"channel": channel},
            bot.logging_context,
        ),
    )
    cached_channel = _get_channel_from_cache(bot, channel)
    if cached_channel:
        return cached_channel
    logger.debug(
        "Channel not in cache.",
        extra=merge_logging_context(
            {"channel": channel},
            bot.logging_context,
        ),
    )
    channel_data = client(bot).api_call("conversations.info", channel=channel)
    if channel_data["ok"]:
        update_channel(bot, channel_data["channel"])
        return channel_data["channel"]
    return {}


def _get_channel_name_from_cache(key, bot_name, value):
    redis_client = omniredis.get_redis_client()
    ret = redis_client.hget(f"{key}:{bot_name}", value)
    if ret is None:
        return None
    else:
        return json.loads(ret)


def get_channel_by_name(bot, channel):
    """
    Get a channel, from its channel name. This function will only fetch from
    cache. If the channel isn't in cache, it will return None.
    """
    if channel.startswith("#"):
        channel = channel[1:]
    redis_client = omniredis.get_redis_client()
    channel_id = redis_client.hget(f"channelsmap:{bot.team.name}", channel)
    if channel_id:
        return _get_channel_name_from_cache("channels", bot.team.name, channel_id)
    group_id = redis_client.hget(f"groupsmap:{bot.team.name}", channel)
    if group_id:
        return _get_channel_name_from_cache("groups", bot.team.name, group_id)
    im_id = redis_client.hget(f"imsmap:{bot.team.name}", channel)
    if im_id:
        return _get_channel_name_from_cache("ims", bot.team.name, im_id)
    mpim_id = redis_client.hget(f"mpimsmap:{bot.team.name}", channel)
    if mpim_id:
        return _get_channel_name_from_cache("mpims", bot.team.name, mpim_id)
    return None


def _get_users(bot, team, max_retries=MAX_RETRIES, sleep=GEVENT_SLEEP_TIME):
    users = []
    retry = 0
    next_cursor = ""
    while True:
        users_data = client(bot).api_call(
            "users.list",
            presence=False,
            limit=1000,
            cursor=next_cursor,
            team_id=team.team_id,
        )
        if users_data["ok"]:
            users.extend(users_data["members"])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= max_retries:
                logger.error(
                    "Exceeded max retries when calling users.list.",
                    extra=bot.logging_context,
                )
                break
            logger.warning(
                "Call to users.list failed, attempting retry",
                extra=merge_logging_context(
                    {"retry": retry},
                    _get_failure_context(users_data),
                    bot.logging_context,
                ),
            )
            gevent.sleep(sleep * retry)
            continue
        next_cursor = users_data.get("response_metadata", {}).get("next_cursor")
        if not next_cursor:
            break
        gevent.sleep(sleep)
    return users


def update_users(bot, team):
    for user in _get_users(bot, team):
        update_user(bot, user)


def update_user(bot, user):
    if user["is_bot"]:
        return
    if user.get("deleted", False):
        return
    profile = user.get("profile")
    if not profile:
        return
    email = profile.get("email")
    if not email:
        return
    name = get_name_from_user(user)
    redis_client = omniredis.get_redis_client()
    redis_client.hset(f"users:{bot.team.name}", user["id"], json.dumps(user))
    redis_client.hset(
        f"usersmap:name:{bot.team.name}",
        name,
        user["id"],
    )
    redis_client.hset(
        f"usersmap:email:{bot.team.name}",
        email,
        user["id"],
    )


def get_users(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter(f"users:{bot.team.name}")


def get_user(bot, user_id):
    """
    Get a user, from its user id
    """
    redis_client = omniredis.get_redis_client()
    user = redis_client.hget(f"users:{bot.team.name}", user_id)
    if user:
        return json.loads(user)
    user = client(bot).api_call("users.info", user=user_id)
    if user["ok"]:
        update_user(bot, user["user"])
        return user["user"]
    else:
        logger.warning(
            "Failed to find user",
            extra=merge_logging_context(
                {"user": user_id},
                bot.logging_context,
            ),
        )
        return {}


def get_name_from_user(user):
    profile = user.get("profile", {})
    name = profile.get("display_name")
    if name:
        return name
    else:
        return user.get("name")


def get_user_by_name(bot, username):
    if username.startswith("@"):
        username = username[1:]
    redis_client = omniredis.get_redis_client()
    user_id = redis_client.hget(f"usersmap:name:{bot.team.name}", username)
    if user_id:
        user_data = redis_client.hget(f"users:{bot.team.name}", user_id)
        if user_data:
            return json.loads(user_data)
    return {}


def get_user_by_email(bot, email):
    redis_client = omniredis.get_redis_client()
    user_id = redis_client.hget(f"usersmap:email:{bot.team.name}", email)
    if user_id:
        user_data = redis_client.hget(f"users:{bot.team.name}", user_id)
        if user_data:
            return json.loads(user_data)
    return {}
