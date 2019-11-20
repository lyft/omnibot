import botocore

import omnibot.services
from omnibot import settings

QUEUE_URL = None
BOTOCORE_CONFIG = botocore.config.Config(
    max_pool_connections=settings.SQS_MAX_POOL_CONNECTIONS
)


def get_client():
    if settings.SQS_URL:
        return omnibot.services.get_boto_client(
            'sqs',
            endpoint_url=settings.SQS_URL,
            config={'name': 'keymanager', 'config': BOTOCORE_CONFIG}
        )
    else:
        return omnibot.services.get_boto_client(
            'sqs',
            config={'name': 'keymanager', 'config': BOTOCORE_CONFIG}
        )


def get_queue_url():
    global QUEUE_URL

    if QUEUE_URL is None:
        client = get_client()
        QUEUE_URL = client.get_queue_url(
            QueueName=settings.SQS_QUEUE_NAME
        )['QueueUrl']

    return QUEUE_URL
