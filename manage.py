#!/usr/bin/env python
import gevent.monkey

gevent.monkey.patch_all()

from flask_script import Manager  # noqa:E402

from omnibot.app import app  # noqa:E402
from omnibot.scripts.utils import CreateSQSQueue  # noqa:E402
from omnibot.scripts.omniredis import PurgeRedis  # noqa:E402

manager = Manager(app)
manager.add_command("create-queues", CreateSQSQueue)
manager.add_command("purge-redis", PurgeRedis)

if __name__ == "__main__":
    manager.run()
