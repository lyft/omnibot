from flask_script import Command

import omnibot.services
from omnibot import settings


class CreateSQSQueue(Command):
    def run(self):
        try:
            sqs = omnibot.services.get_boto_client(
                'sqs',
                endpoint_url=settings.SQS_URL
            )
            print(sqs.create_queue(QueueName=settings.SQS_QUEUE_NAME))
        except Exception:
            print('Failed to create queue')
            return 1
