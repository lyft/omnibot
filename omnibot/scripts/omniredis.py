from flask_script import Command

from omnibot import settings
from omnibot.services import omniredis


class PurgeRedis(Command):
    def run(self):
        redis_client = omniredis.get_redis_client()
        for team in settings.SLACK_TEAMS:
            redis_client.delete('channels:{}'.format(team))
            redis_client.delete('channelsmap:{}'.format(team))
            redis_client.delete('groups:{}'.format(team))
            redis_client.delete('groupsmap:{}'.format(team))
            redis_client.delete('ims:{}'.format(team))
            redis_client.delete('imsmap:{}'.format(team))
            redis_client.delete('mpims:{}'.format(team))
            redis_client.delete('mpimsmap:{}'.format(team))
            redis_client.delete('users:{}'.format(team))
        redis_client.delete('teams')
