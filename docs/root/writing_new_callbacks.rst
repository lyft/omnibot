##############################
Writing new callback functions
##############################

Callbacks are part of a handler configuration. When a handler is matched, the defined callback will be called with the payload container for the handler type, and with whatever arguments are defined as part of the callback. As an example, let's take a look at an example handler configuration, with an existing callback function:

.. code-block:: yaml

   message_handlers:
     - match: "event"
       match_type: "command"
       description: "create events using eventbot"
       bots:
         "your-team-name-here":
           - "omnibot"
       callbacks:
         - module: "omnibot.callbacks.network_callbacks:http_callback"
           kwargs:
             request_kwargs:
               url: "http://eventbot/api/v1/eventbot"

.. code-block:: python

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

The handler config specifies the callback module, and the function within the module in format ``path.to.module:function_name``. The config also has a mechanism to pass keyword arguments into the function, from the configuration. In this particular case, the configuration is passing a dictionary into the ``request_kwargs`` keyword argument.

A callback is just a function within a python module, which requires a positional argument, which is by convention named ``container``, and can accept any keyword arguments you'd like to define, which are passed in from the configuration.

Callback functions should always return a dictionary. The return format is dependent on the type of handler, and is defined in the :doc:`slack proxying documentation <slack_proxying>`.

Let's look at a more explicit example of a handler/callback combo that directly responds to an event, rather than proxying a backend service:

.. code-block:: yaml

   slash_command_handlers:
     - command: '/tableflip'
       response_type: 'ephemeral'
       bots:
         "lyft-test-sandbox":
           - "omnibot"
       callbacks:
         - module: "omnibot.callbacks.slash_command_callbacks:tableflip_callback"

.. code-block:: python

    def tableflip_callback(container):
        """
        Respond back with a tableflip
        """
        payload = container.payload
        logger.debug('tableflip callback payload: {}'.format(
            json.dumps(payload, indent=2))
        )
        return {
            # Respond back to the slash command with the same text
            'responses': [
                {
                    'response_type': 'in_channel',
                    'text': '(╯°□°)╯︵ ┻━┻'
                }
            ]
        }

Notice in this example, that the handler is matching for a particular slash command, sending that into a function with no arguments, and the callback function is simply responding with the response that should occur for the slash command.
