import logging

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

SESSION = None


# TODO: Accept params and memoize using functools
def _get_requests_session():
    global SESSION
    if SESSION is None:
        SESSION = requests.Session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        SESSION.mount('http://', adapter)
        SESSION.mount('https://', adapter)
    return SESSION


def http_callback(container, request_kwargs=None, client_kwargs=None):
    # TODO: support client kwargs
    if client_kwargs is None:
        client_kwargs = {}
    if request_kwargs is None:
        logger.error(
            'http_callback called without request_kwargs',
            extra=container.event_trace
        )
        return {}
    client = _get_requests_session()
    url = request_kwargs['url']

    # request_kwargs is a reference to the global settings,
    # so changing it changes the global settings, which we don't
    # want to do. Instead of changing request_kwargs, we make a
    # copy of it, and change the copy by removing the 'url' field.
    kwargs = {k: v for k, v in request_kwargs.items() if k != 'url'}

    try:
        response = client.post(
            url,
            json=container.payload,
            **kwargs
        )
    except RequestException as e:
        logger.error(
            'Failed to make request to {} with error: {}'.format(
                url,
                str(e)
            )
        )
        return {}
    if response.status_code != requests.codes.ok:
        msg = 'Got status code {0} for {1}, with response: {2}'
        logger.error(
            msg.format(
                response.status_code,
                url,
                response.text
            ),
            extra=container.event_trace
        )
    return response.json()
