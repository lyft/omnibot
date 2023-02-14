from flask_script import Command

from omnibot import settings
from omnibot.services import omniredis


class PurgeRedis(Command):
    def run(self):
        redis_client = omniredis.get_redis_client()
        for team in settings.SLACK_TEAMS:
            redis_client.delete(f"channels:{team}")
            redis_client.delete(f"channelsmap:{team}")
            redis_client.delete(f"groups:{team}")
            redis_client.delete(f"groupsmap:{team}")
            redis_client.delete(f"ims:{team}")
            redis_client.delete(f"imsmap:{team}")
            redis_client.delete(f"mpims:{team}")
            redis_client.delete(f"mpimsmap:{team}")
            redis_client.delete(f"users:{team}")
        redis_client.delete("teams")
