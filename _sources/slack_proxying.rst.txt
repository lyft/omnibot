.. _ref-slack-proxing:

##############
Slack proxying
##############

****************
Message handlers
****************

When omnibot routes messages to your handler, the handler doesn't need to talk to slack; omnibot will do that for you. Just respond with a list of actions for omnibot to take on your behalf. The actions are just `slack api calls <https://api.slack.com/methods>`_ you'd make:

.. code-block:: json

    {
        "actions":
        [
            {
                "action": "chat.postMessage",
                "kwargs": {
                    "text": "Please do not use @here."
                }
            },
            {
                "action": "reactions.add",
                "kwargs": {
                    "name": "broken_heart"
                }
            }
        ]
    }

``action`` is the API call to make, and ``kwargs`` is the key word arguments you'd pass into that API call.

Note that normally for most actions you'd need to include ``channel`` or ``thread_ts``, but omnibot will automatically fill those in with the current ``channel`` and ``thread_ts``, unless you override it. By default omnibot will always use a ``thread_ts``, responding to messages using a thread; if you'd like to respond in the channel, rather than in a thread, you can set ``thread_ts`` to None.

When you send messages through the API, you need to use slack message format for things like links, channels, users, specials, etc.. Omnibot can handle these for you, if you'd like. To have omnibot parse your message into the right format, send the ``omnibot_parse`` keyword arg into the kwargs. ``omnibot_parse`` is a dict, mapping the field you want to parse with what you want parsed. For instance, let's let omnibot parse the above message for us:

.. code-block:: json

    {
        "actions":
        [
            {
                "action": "chat.postMessage",
                "kwargs": {
                    "text": "Please do not use @here.",
                    "omnibot_parse": {"text": ["specials"]}
                }
            },
            {
                "action": "reactions.add",
                "kwargs": {
                    "name": "broken_heart"
                }
            }
        ]
    }

If the message isn't parsed, then the ``@here`` in the above message would show as plain text. We're now telling omnibot to parse the text kwarg and replace any special it finds (``@here``) with the slack formatted version (``<!here|here>``).

************************************************
Slash command and interactive component handlers
************************************************

When omnibot routes slash commands or interactive component events to your handler, the handler doesn't need to talk to slack; omnibot can do that for you. Just respond with a list of responses for omnibot to send back to the ``response_url`` on your behalf. The responses are just `standard responses <https://api.slack.com/slash-commands#responding_to_a_command>`_ you'd give back to the slash command or interactive component APIs:

.. code-block:: json

    {
        "responses":
        [
            {
                "text": "pong",
                "attachments": [
                    {
                        "text": "Look at this game of ping pong over @here"
                    }
                ]
            },
            {
                "response_type": "ephemeral",
                "text": "a private pong"
            }
        ]
    }

Note that if you do not provide a response_type in the response, the default will be what's set for the handler; if the handler doesn't have response_type set, it defaults to ephemeral.

When you respond, you need to use slack message format for things like links, channels, users, specials, etc.. Omnibot can handle these for you, if you'd like. To have omnibot parse your message into the right format, send the ``omnibot_parse`` keyword arg into the response. ``omnibot_parse`` is a dict, mapping the field you want to parse with what you want parsed. For instance, let's let omnibot parse the above message for us:

.. code-block:: json

    {
        "responses":
        [
            {
                "text": "pong",
                "attachments": [
                    {
                        "text": "Look at this game of ping pong over @here"
                    }
                ],
                "omnibot_parse": {"text": ["specials"]}
            },
            {
                "response_type": "ephemeral",
                "text": "a private pong"
            }
        ]
    }

If the text isn't parsed, then the ``@here`` in the above response would show as plain text. We're now telling omnibot to parse the text kwarg and replace any special it finds (``@here``) with the slack formatted version (``<!here|here>``).

Unlike messages, it's possible for your handler to respond directly to slash command or interactive component events, rather than needing to go back through omnibot. The ``response_url`` provided in the payload sent to your handler can be used to send responses. For each response you'd like to send, you'll need to send it as a POST payload to the ``response_url``. Remember, though, that you'll need to send text in slack message format, which will require you to do your own parsing. Check out omnibot's API for endpoints you can use to do basic parsing or lookups.

It's also possible to ask omnibot to do a set of actions for you, as well; for instance:

.. code-block:: json

    {
        "responses":
        [
            {
                "text": "pong",
                "attachments": [
                    {
                        "text": "Look at this game of ping pong over @here"
                    }
                ]
            },
        ],
        "actions": [
            {
                "action": "chat.postMessage",
                "kwargs": {
                    "channel": "pong",
                    "text": "Someone pinged!",
                    "omnibot_parse": {
                        "channel": ["channels"]
                    }
                }
            }
        ]
    }

The above will respond back to the slash command or interactive component, but it will also post a message into the pong channel on your behalf.
