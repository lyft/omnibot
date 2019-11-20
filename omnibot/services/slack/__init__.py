"""
Slackclient wrapper.
"""
import json
import logging

import gevent
import slackclient

from omnibot.services import omniredis

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
GEVENT_SLEEP_TIME = 5

# TODO: locking for long-running updates
_client = {}


def client(bot, client_type='oauth'):
    """
    Global Slack client.
    """
    global _client
    team_name = bot.team.name
    if team_name not in _client:
        _client[team_name] = {}
    if bot.name not in _client[team_name]:
        _client[team_name][bot.name] = {
            'oauth': slackclient.SlackClient(
                bot.oauth_token
            )
        }
        if bot.oauth_bot_token:
            _client[team_name][bot.name]['oauth_bot'] = slackclient.SlackClient(
                bot.oauth_bot_token
            )
    if client_type == 'oauth_bot':
        try:
            return _client[team_name][bot.name]['oauth_bot']
        except KeyError:
            pass
    return _client[team_name][bot.name]['oauth']


def _get_channels(bot):
    """
    Get all channels
    """
    channels = []
    retry = 0
    next_cursor = ''
    while True:
        channels_data = client(bot, client_type='oauth_bot').api_call(
            'channels.list',
            exclude_archived=True,
            exclude_members=True,
            limit=1000,
            cursor=next_cursor
        )
        if channels_data['ok']:
            channels.extend(channels_data['channels'])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error(
                    'Exceeded max retries when calling channels.list.'
                )
                break
            logger.warning(
                'Call to channels.list failed, attempting'
                ' retry #{retry}: {error}'.format(
                    retry=retry,
                    error=channels_data.get('error')
                )
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
        next_cursor = channels_data.get(
            'response_metadata',
            {}
        ).get('next_cursor')
        if not next_cursor:
            break
        gevent.sleep(GEVENT_SLEEP_TIME)
    return channels


def update_channels(bot):
    for channel in _get_channels(bot):
        update_channel(bot, channel)


def update_channel(bot, channel):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(
        'channels:{}'.format(bot.team.name),
        channel['id'],
        json.dumps(channel)
    )
    redis_client.hset(
        'channelsmap:{}'.format(bot.team.name),
        channel['name'],
        channel['id'],
    )


def get_channels(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter('channels:{}'.format(bot.team.name))


def _get_groups(bot):
    """
    Get all private channels
    """
    groups = []
    retry = 0
    next_cursor = ''
    while True:
        groups_data = client(bot, client_type='oauth_bot').api_call(
            'groups.list',
            limit=1000,
            cursor=next_cursor
        )
        if groups_data['ok']:
            groups.extend(groups_data['groups'])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error('Exceeded max retries when calling groups.list.')
                break
            logger.warning(
                'Call to groups.list failed, attempting'
                ' retry #{retry}: {error}'.format(
                    retry=retry,
                    error=groups_data.get('error')
                )
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
        next_cursor = groups_data.get(
            'response_metadata',
            {}
        ).get('next_cursor')
        if not next_cursor:
            break
        gevent.sleep(GEVENT_SLEEP_TIME)
    return groups


def update_groups(bots):
    for bot in bots:
        for group in _get_groups(bot):
            update_group(bot, group)


def update_group(bot, group):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(
        'groups:{}'.format(bot.team.name),
        group['id'],
        json.dumps(group)
    )
    redis_client.hset(
        'groupsmap:{}'.format(bot.team.name),
        group['name'],
        group['id'],
    )


def get_groups(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter('groups:{}'.format(bot.team.name))


def _get_ims(bot):
    """
    Get all im channels
    """
    ims = []
    retry = 0
    next_cursor = ''
    while True:
        im_data = client(bot, client_type='oauth_bot').api_call(
            'im.list',
            limit=1000,
            cursor=next_cursor
        )
        if im_data['ok']:
            ims.extend(im_data['ims'])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error('Exceeded max retries when calling im.list.')
                break
            logger.warning(
                'Call to im.list failed, attempting'
                ' retry #{retry}: {error}'.format(
                    retry=retry,
                    error=im_data.get('error')
                )
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
        next_cursor = im_data.get('response_metadata', {}).get('next_cursor')
        if not next_cursor:
            break
        gevent.sleep(GEVENT_SLEEP_TIME)
    return ims


def update_ims(bots):
    for bot in bots:
        for im in _get_ims(bot):
            update_im(bot, im)


def update_im(bot, im):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(
        'ims:{}'.format(bot.team.name),
        im['id'],
        json.dumps(im)
    )
    redis_client.hset(
        'imsmap:{}'.format(bot.team.name),
        im['user'],
        im['id'],
    )


def get_ims(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter('ims:{}'.format(bot.team.name))


def get_im_channel_id(bot, user_id):
    redis_client = omniredis.get_redis_client()
    imsmap_id = redis_client.hget('imsmap:{}'.format(bot.team.name), user_id)
    if imsmap_id:
        raw_im = redis_client.hget('ims:{}'.format(bot.team.name), imsmap_id)
        if raw_im:
            im = json.loads(raw_im)
            if not im['is_user_deleted']:
                return im['id']

    retry = 0
    while True:
        users = user_id
        conversation_data = client(bot, client_type='oauth_bot').api_call(
            'conversations.open',
            users=users
        )
        if conversation_data['ok']:
            return conversation_data['channel']['id']
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error('Exceeded max retries when calling conversations.open.')
                break
            logger.warning(
                'Call to conversations.open failed, attempting'
                ' retry #{retry}: {error}'.format(
                    retry=retry,
                    error=conversation_data.get('error')
                )
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
    return None


def _get_mpims(bot):
    """
    Get all mpim channels
    """
    mpims = []
    retry = 0
    next_cursor = ''
    while True:
        mpim_data = client(bot, client_type='oauth_bot').api_call(
            'mpim.list',
            limit=1000,
            cursor=next_cursor
        )
        if mpim_data['ok']:
            mpims.extend(mpim_data['groups'])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= MAX_RETRIES:
                logger.error('Exceeded max retries when calling mpim.list.')
                break
            logger.warning(
                'Call to mpim.list failed, attempting'
                ' retry #{retry}: {error}'.format(
                    retry=retry,
                    error=mpim_data.get('error')
                )
            )
            gevent.sleep(GEVENT_SLEEP_TIME)
            continue
        next_cursor = mpim_data.get('response_metadata', {}).get('next_cursor')
        if not next_cursor:
            break
        gevent.sleep(GEVENT_SLEEP_TIME)
    return mpims


def update_mpims(bots):
    for bot in bots:
        for mpim in _get_mpims(bot):
            update_mpim(bot, mpim)


def update_mpim(bot, mpim):
    redis_client = omniredis.get_redis_client()
    redis_client.hset(
        'mpims:{}'.format(bot.team.name),
        mpim['id'],
        json.dumps(mpim)
    )
    redis_client.hset(
        'mpimsmap:{}'.format(bot.team.name),
        mpim['name'],
        mpim['id'],
    )


def get_mpims(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter('mpims:{}'.format(bot.team.name))


def _get_emoji(bot):
    # TODO: split this retry logic into a generic retry function
    for retry in range(MAX_RETRIES):
        resp = client(bot).api_call('emoji.list')
        if resp['ok']:
            break
        logger.warning(
            'Call to emoji.list failed, attempting'
            ' retry #{retry}: {error}'.format(
                retry=retry,
                error=resp.get('error')
            )
        )
        gevent.sleep(GEVENT_SLEEP_TIME)
    else:
        logger.error('Exceeded max retries when calling emoji.list.')
        return {}

    emoji = {}
    for k, v in resp['emoji'].items():
        while v.startswith('alias:'):
            _, _, alias = v.partition(':')
            v = resp['emoji'].get(alias, '')
        if v:
            emoji[k] = v
    return emoji


def update_emoji(bot):
    redis_client = omniredis.get_redis_client()
    for k, v in _get_emoji(bot).items():
        redis_client.hset('emoji:{}'.format(bot.team.name), k, v)


def get_emoji(bot, name):
    redis_client = omniredis.get_redis_client()
    return redis_client.hget('emoji:{}'.format(bot.team.name), name)


def _get_channel_from_cache(bot, channel):
    redis_client = omniredis.get_redis_client()
    channel_data = redis_client.hget(
        'channels:{}'.format(bot.team.name),
        channel
    )
    if channel_data:
        return json.loads(channel_data)
    group_data = redis_client.hget('groups:{}'.format(bot.team.name), channel)
    if group_data:
        return json.loads(group_data)
    im_data = redis_client.hget('ims:{}'.format(bot.team.name), channel)
    if im_data:
        return json.loads(im_data)
    mpim_data = redis_client.hget('mpims:{}'.format(bot.team.name), channel)
    if mpim_data:
        return json.loads(mpim_data)
    return None


def get_channel(bot, channel):
    """
    Get a channel, from its channel id
    """
    logger.debug('Fetching channel: {}'.format(channel))
    cached_channel = _get_channel_from_cache(bot, channel)
    if cached_channel:
        return cached_channel
    logger.debug('Channel {} not in cache.'.format(channel))
    channel_data = client(bot).api_call(
        'channels.info',
        channel=channel
    )
    if channel_data['ok']:
        update_channel(bot, channel_data['channel'])
        return channel_data['channel']
    logger.debug(
        'Channel {} is not a public channel, looking for'
        ' private channel.'.format(channel)
    )
    # no channel, look for a private channel
    group_data = client(bot, client_type='oauth_bot').api_call(
        'groups.info',
        channel=channel
    )
    if group_data['ok']:
        update_group(bot, group_data['group'])
        return group_data['group']
    logger.debug(
        'Channel {} is not a private channel, skipping lookup'
        ' for IMs.'.format(channel)
    )
    # OK. At this point it must either be an IM or MPIM that's brand new.
    # We'll need to refresh and look in cache.
    # Let's check IMs first.
    update_ims([bot])
    cached_channel = _get_channel_from_cache(bot, channel)
    if cached_channel:
        return cached_channel
    # Now let's refresh and check MPIMs
    update_mpims([bot])
    cached_channel = _get_channel_from_cache(bot, channel)
    if cached_channel:
        return cached_channel
    logger.warning(
        'Failed to find channel={} via bot={}'.format(channel, bot.name)
    )
    return {}


def _get_channel_name_from_cache(key, bot_name, value):
    redis_client = omniredis.get_redis_client()
    ret = redis_client.hget('{}:{}'.format(key, bot_name), value)
    if ret is None:
        return None
    else:
        return json.loads(ret)


def get_channel_by_name(bot, channel):
    """
    Get a channel, from its channel name. This function will only fetch from
    cache. If the channel isn't in cache, it will return None.
    """
    if channel.startswith('#'):
        channel = channel[1:]
    redis_client = omniredis.get_redis_client()
    channel_id = redis_client.hget(
        'channelsmap:{}'.format(bot.team.name),
        channel
    )
    if channel_id:
        return _get_channel_name_from_cache(
            'channels',
            bot.team.name,
            channel_id
        )
    group_id = redis_client.hget('groupsmap:{}'.format(bot.team.name), channel)
    if group_id:
        return _get_channel_name_from_cache('groups', bot.team.name, group_id)
    im_id = redis_client.hget('imsmap:{}'.format(bot.team.name), channel)
    if im_id:
        return _get_channel_name_from_cache('ims', bot.team.name, im_id)
    mpim_id = redis_client.hget('mpimsmap:{}'.format(bot.team.name), channel)
    if mpim_id:
        return _get_channel_name_from_cache('mpims', bot.team.name, mpim_id)
    return None


def _get_users(bot, max_retries=MAX_RETRIES, sleep=GEVENT_SLEEP_TIME):
    users = []
    retry = 0
    next_cursor = ''
    while True:
        users_data = client(bot, client_type='oauth_bot').api_call(
            'users.list',
            presence=False,
            limit=1000,
            cursor=next_cursor
        )
        if users_data['ok']:
            users.extend(users_data['members'])
        else:
            # TODO: split this retry logic into a generic retry function
            retry = retry + 1
            if retry >= max_retries:
                logger.error('Exceeded max retries when calling users.list.')
                break
            logger.warning(
                'Call to users.list failed, attempting'
                ' retry #{retry}: {error}'.format(
                    retry=retry,
                    error=users_data.get('error')
                )
            )
            gevent.sleep(sleep * retry)
            continue
        next_cursor = users_data.get(
            'response_metadata',
            {}
        ).get('next_cursor')
        if not next_cursor:
            break
        gevent.sleep(sleep)
    return users


def update_users(bot):
    for user in _get_users(bot):
        update_user(bot, user)


def update_user(bot, user):
    if user['is_bot']:
        return
    if user['deleted']:
        return
    profile = user.get('profile')
    if not profile:
        return
    email = profile.get('email')
    if not email:
        return
    name = get_name_from_user(user)
    redis_client = omniredis.get_redis_client()
    redis_client.hset(
        'users:{}'.format(bot.team.name), user['id'], json.dumps(user)
    )
    redis_client.hset(
        'usersmap:name:{}'.format(bot.team.name),
        name,
        user['id'],
    )
    redis_client.hset(
        'usersmap:email:{}'.format(bot.team.name),
        email,
        user['id'],
    )


def get_users(bot):
    redis_client = omniredis.get_redis_client()
    return redis_client.hscan_iter('users:{}'.format(bot.team.name))


def get_user(bot, user_id):
    """
    Get a user, from its user id
    """
    redis_client = omniredis.get_redis_client()
    user = redis_client.hget('users:{}'.format(bot.team.name), user_id)
    if user:
        return json.loads(user)
    user = client(bot).api_call(
        'users.info',
        user=user_id
    )
    if user['ok']:
        update_user(bot, user['user'])
        return user['user']
    else:
        logger.warning('Failed to find user={} via bot={}.'.format(
            user_id,
            bot
        ))
        logger.error(user)
        return {}


def get_name_from_user(user):
    profile = user.get('profile', {})
    name = profile.get('display_name')
    if name:
        return name
    else:
        return user.get('name')


def get_user_by_name(bot, username):
    if username.startswith('@'):
        username = username[1:]
    redis_client = omniredis.get_redis_client()
    user_id = redis_client.hget(
        'usersmap:name:{}'.format(bot.team.name),
        username
    )
    if user_id:
        user_data = redis_client.hget(
            'users:{}'.format(bot.team.name),
            user_id
        )
        if user_data:
            return json.loads(user_data)
    return {}


def get_user_by_email(bot, email):
    redis_client = omniredis.get_redis_client()
    user_id = redis_client.hget(
        'usersmap:email:{}'.format(bot.team.name),
        email
    )
    if user_id:
        user_data = redis_client.hget(
            'users:{}'.format(bot.team.name),
            user_id
        )
        if user_data:
            return json.loads(user_data)
    return {}
