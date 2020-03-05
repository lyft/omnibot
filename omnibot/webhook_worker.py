import gevent
import gevent.monkey
gevent.monkey.patch_all(thread=False)
import gevent.pool # noqa:E402
import signal # noqa:E402
import json # noqa:E402
import logging # noqa:E402
import time # noqa:E402

import botocore # noqa:E402

from omnibot import settings # noqa:E402
from omnibot import processor # noqa:E402
from omnibot.services import stats # noqa:E402
from omnibot.services import slack # noqa:E402
from omnibot.services import sqs # noqa:E402
from omnibot.services.slack.team import Team # noqa:E402
from omnibot.services.slack.bot import Bot # noqa:E402

STATE = {
    'shutdown': False
}


def wait_available(pool, pool_name):
    statsd = stats.get_statsd_client()
    if pool.full():
        statsd.incr('%s.pool.full' % pool_name)
        pool.wait_available()


def delete_message(client, queue_url, message):
    client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )


def _instrument_message_latency(event):
    statsd = stats.get_statsd_client()
    event_sent_time_ms = int(float(event['event_ts']) * 1000)
    now = int(time.time() * 1000)
    statsd.timing('delivery_latency', now - event_sent_time_ms)


def handle_message(client, queue_url, message):
    statsd = stats.get_statsd_client()
    with statsd.timer('handle_message'):
        attrs = message['MessageAttributes']
        if 'type' not in attrs:
            logger.error('SQS message does not have a type attribute.')
            delete_message(client, queue_url, message)
            return
        m_type = attrs['type']['StringValue']
        if m_type not in ['event', 'slash_command', 'interactive_component']:
            delete_message(client, queue_url, message)
            logger.error(
                '{} is an unsupported message type.'.format(m_type)
            )
            return
        if 'version' not in attrs:
            version = 1
        else:
            version = int(attrs['version']['StringValue'])
        logger.debug('Received SQS message of type {}'.format(m_type))
        try:
            if version == 2:
                event = json.loads(message['Body'])['event']
                if m_type == 'event':
                    _instrument_message_latency(event['event'])
                    processor.process_event(event)
                elif m_type == 'slash_command':
                    processor.process_slash_command(event)
                elif m_type == 'interactive_component':
                    processor.process_interactive_component(event)
            else:
                logger.error(
                    '{} is an unsupported message version.'.format(version)
                )
        except Exception:
            logger.exception(
                'Failed to handle webhook SQS message',
                exc_info=True
            )
            return
        delete_message(client, queue_url, message)


def handle_messages(client, queue_url, queue_pool):
    global STATE
    statsd = stats.get_statsd_client()

    while not STATE['shutdown']:
        try:
            response = client.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['SentTimestamp'],
                MaxNumberOfMessages=settings.SQS_BATCH_SIZE,
                MessageAttributeNames=['All'],
                VisibilityTimeout=settings.SQS_VISIBILITY_TIMEOUT,
                WaitTimeSeconds=settings.SQS_WAIT_TIME_SECONDS
            )
            if 'Messages' in response:
                statsd.incr('sqs.received', len(response['Messages']))
                for message in response['Messages']:
                    with statsd.timer('webhookpool.spawn'):
                        wait_available(queue_pool, 'webhookpool')
                        queue_pool.spawn(
                            handle_message,
                            client,
                            queue_url,
                            message
                        )
            else:
                logger.debug('No messages, continuing')
        except botocore.parsers.ResponseParserError:
            logger.warning('Got a bad response from SQS, continuing.')
        except Exception:
            logger.exception('General error', exc_info=True)


def main():
    client = sqs.get_client()
    queue_url = sqs.get_queue_url()
    queue_pool = gevent.pool.Pool(settings.WEBHOOK_WORKER_CONCURRENCY)
    handle_messages(client, queue_url, queue_pool)


if __name__ == "__main__":
    from omnibot import setup_logging  # noqa:F401
    logger = logging.getLogger(__name__)
    main()
