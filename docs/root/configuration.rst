#############
Configuration
#############

*****************************
Example Minimal Configuration
*****************************

``omnibot.env``:

.. code-block:: bash

    CREDENTIALS_SLACK_OAUTH_BOT_TOKEN_A87654321=xoxb-...
    CREDENTIALS_SLACK_OAUTH_TOKEN_A87654321=xoxp-...
    CREDENTIALS_SLACK_VERIFICATION_TOKEN_A87654321=...
    AWS_DEFAULT_REGION=us-east-1
    # AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are not required, if this is accessible from the metadata service
    AWS_ACCESS_KEY_ID=1
    AWS_SECRET_ACCESS_KEY=1
    # LOG_CONFIG_FILE isn't required, but watcher and webhook workers will have minimum and unformatted log output otherwise
    LOG_CONFIG_FILE=/etc/omnibot/logging.yaml
    REDIS_HOST=redis
    SQS_QUEUE_NAME=omnibot
    SQS_URL=http://sqs:9203

``omnibot.conf``:

.. code-block:: yaml

    authorization:
      checks:
        - module: "omnibot.authnz:allowed_paths"
          kwargs:
            paths:
              - "/api/v1/slack/event"
              - "/api/v1/slack/slash_command"
              - "/api/v1/slack/interactive"
    teams:
      "example-team": "T12345678"
    bots:
      "example-team":
        "example-bot": "A87654321"
    primary_bot:
      "example-team": "example-bot"
    handlers:
      message_handlers:
        - match: ""
          match_type: "command"
          match_mention: True
          description: "testing"
          bots:
            "example-team":
              - "example-bot"
          callbacks:
            - module: "omnibot.callbacks.message_callbacks:test_callback"
              kwargs:
                text: 'test'

*******************
Basic Configuration
*******************

Configuration File Configuration
================================

A majority of omnibot's configuration comes from a configuration file, which can be configured through an environment variable:

* ``CONFIG_FILE`` (optional): Filesystem location of omnibot's configuration file. Default: ``/etc/omnibot/omnibot.conf``

For basic functionality, omnibot will need to know about the teams and bots it will be proxying on behalf of. Omnibot can support multiple teams and multiple bots inside of those teams.

Teams
=====

Teams are configured in omnibot's configuration file, as a dictionary mapping of team names (used by omnibot) to team IDs (used by slack):

.. code-block:: yaml

    teams:
      "example-production": "T1234ABCD"
      "example-sandbox": "T4321DCBA"

Bots
====

See :doc:`docs for adding slack apps <adding_new_slack_apps>` for how to add a slack app for use in this section.

Bots are configured in omnibot's configuration file, as a dictionary of dictionaries, mapping teams to bots, and bots to IDs:

.. code-block:: yaml

    bots:
      "example-production":
        "omnibot": "A1111AAAA"
        "docbot": "A1234ABCD"
        "deploybot": "A4321DCBA"
      "example-sandbox":
        "omnibot": "A6666ZZZZ"
        "docbot": "A6789WXYZ"
        "deploybot": "A9876ZYXW"

For parts of omnibot's functionality, it's necessary to poll slack's APIs for users, channels, private channels (groups), and some other data sets. To reduce the number of API calls necessary, and to be able to limit oauth scopes where possible, omnibot uses a ``primary bot`` per team to fetch this data (note that it doesn't need to be named omnibot, use any bot you want):

.. code-block:: yaml

    primary_bot:
      "example-production": "omnibot"
      "example-sandbox": "omnibot"

Bot Credential Configuration
============================

Credentials for bots in omnibot are configured through environment variables. For each bot, it's necessary to set three environment variables:

* ``CREDENTIALS_SLACK_VERIFICATION_TOKEN_<APP_ID>``
* ``CREDENTIALS_SLACK_OAUTH_TOKEN_<APP_ID>``
* ``CREDENTIALS_SLACK_OAUTH_BOT_TOKEN_<APP_ID>``

So, in the above configuration, for omnibot, in ``example-production``, we'd set:

.. code-block:: bash

    export CREDENTIALS_SLACK_VERIFICATION_TOKEN_A1111AAAA="..."
    export CREDENTIALS_SLACK_OAUTH_TOKEN_A1111AAAA="xoxp..."
    export CREDENTIALS_SLACK_OAUTH_BOT_TOKEN_A1111AAAA="xoxb..."

URLs Configuration for Use in Slack App Dashboard
=================================================

omnibot currently has support for accepting events, slash commands, and interactive components. The following API endpoints are used:

* ``events``: ``/api/v1/slack/event`` (Example: ``https://example.com/api/v1/slack/event``)
* ``slash commands``: ``/api/v1/slack/slash_command`` (Example: ``https://example.com/api/v1/slack/slash_command``)
* ``interactive components``: ``/api/v1/slack/interactive`` (Example: ``https://example.com/api/v1/slack/interactive``)

SQS Configuration
=================

omnibot enqueues every event it receives from slack. Worker processes handle the SQS messages. omnibot cannot operate without SQS. SQS settings are configured through environnent variables:

* ``SQS_QUEUE_NAME`` (required): SQS queue name to use for enqueuing slack events
* ``WEBHOOK_WORKER_CONCURRENCY`` (recommended): gevent pool concurrency for handling enqueued webhooks. Default: ``10``
* ``SQS_URL`` (optional): A non-default URL to use, if you're not connecting directly to SQS, but instead are using a proxy like envoy, or some SQS replacement or development service.
* ``SQS_BATCH_SIZE`` (optional): Number of SQS events to fetch per request. Default: same as ``WEBHOOK_WORKER_CONCURRENCY``, if ``WEBHOOK_WORKER_CONCURRENCY`` is less than or equal to 10, otherwise ``10``
* ``SQS_MAX_POOL_CONNECTIONS`` (optional): ``max_pool_connections`` in botocore configuration. Default: ``WEBHOOK_WORKER_CONCURRENCY`` or ``10``, whichever is lower.
* ``SQS_VISIBILITY_TIMEOUT`` (optional): Amount of time an SQS message will remain invisible to other webhook workers, when a webhook worker dequeues an event. Recommended to leave at default. Default: ``60``
* ``SQS_WAIT_TIME_SECONDS`` (optional): SQS long polling rate. Recommended to leave at default. Default: ``1``

For production workloads, you may want to increase ``WEBHOOK_WORKER_CONCURRENCY``, depending on the number of webhook worker processes you're running. omnibot uses gevent, so, you'll want to adjust this based on the number of webhook worker processes you're running, the number of hosts running the webhook workers, and the number of events per second you'll be handling. At the time of this writing, Lyft is using a setting of 10 in production, running 3 hosts, with 1 webhook worker process per host.

Redis Configuration
===================

omnibot uses a redis queue for an ephemeral cache that's partially populated as a read-through cache, and also continually repopulated through a ``watcher`` worker process. omnibot cannot operate without redis. Configuration for redis is configured through environment variables:

* ``REDIS_HOST``: The hostname for your redis server, or envoy/nutcracker proxy. Default: ``localhost``
* ``REDIS_PORT``: The port for your redis server, or envoy/nutcracker proxy. Default: ``6379``

Statsd Configuration
====================

omnibot has relatively rich instrumentation (see the :ref:`observability docs <observability_stats>` for more information); metrics are sent through pystatsd, which is configured through environment variables:

* ``STATSD_HOST``: The host for your statsd server. Default: ``localhost``
* ``STATSD_PORT``: The port for your statsd server. Default: ``8125``
* ``STATSD_PREFIX``: A prefix to use for all metrics sent. Default: ``omnibot``

Logging Configuration
=====================

Logging is primarily assumed to be configured through your wsgi server (like gunicorn or uwsgi) for the web worker. For the watcher and webhook workers, you can define the configuration via a python dict config:

* ``LOG_CONFIG_FILE``: Path to a yaml or json file that defines your logging config. Default: ``/etc/omnibot/logging.conf``

See the :ref:`observability docs <observability_logs>` for information about using logs for tracing events.

.. _handler_configuration:

*********************
Handler Configuration
*********************

All handler configurations are configured through the omnibot configuration file.

Common Handler Configuration
============================

Though omnibot has a number of handler configurations, they're all roughly configurations that route something sent from slack, to a function that handles it. There's some common configuration that defines part of this across all handler types. For example, here's a message handler that is routing messages with the text ``@here`` or ``@channel``, to a built-in callback function:

.. code-block:: yaml

    message_handlers:
      - match: ".*(@here|@channel).*"
        match_type: "regex"
        description: "Warn on @here or @channel."
        bots:
          "example-production":
            - "omnibot"
        callbacks:
          - module: "omnibot.callbacks.message_callbacks:specials_callback"
            kwargs:
              channels:
                random:
                  message: "Please don't `{special}` as it notifies {member_count} people."
                  reaction: "broken_heart"

Bots is a dictionary of teams with a list of bots, so it's possible to use the same callback for multiple teams, and multiple bots in those teams. Also, callbacks is a list, so it's possible to route the same message to multiple callbacks:

.. code-block:: yaml

    message_handlers:
      - match: ".*(@here|@channel).*"
        match_type: "regex"
        description: "Warn on @here or @channel."
        bots:
          "example-production":
            - "omnibot"
          "example-sandbox":
            - "omnibot"
        callbacks:
          - module: "omnibot.callbacks.message_callbacks:specials_callback"
            kwargs:
              channels:
                random:
                  message: "Please don't `{special}` as it notifies {member_count} people."
                  reaction: "broken_heart"
          - module: "omnibot.callbacks.network_callbacks:http_callback"
            kwargs:
              request_kwargs:
                url: "https://herebot.local/api/v1/herebot/messages"

``bots`` is a dict of teams, each team specifying a list of bots that this handler targets. Any team/bot not listed here will be ignored.

``callbacks`` is a list of functions that will be called (in order) if this handler matches. Each callback is specified by a ``module``, which is a ``python.path.to.the.module:a_function_in_the_module``, and ``kwargs``, which is a dictionary of keys and values to pass into the function. For example, ``special_callback`` is defined like so::

    def specials_handler(channels):
        ...

For ``kwargs``, see the documentation specific to the callback to see what you can pass in.

``description`` is used to document the handler, and also, in some cases, to populate auto-generated help responses from the bots.

Message Handlers
================

Message handlers route slack messages (via event subscriptions) from a list of bots in a particular team to callback functions, when the message matches certain criteria. Message handlers match in two different ways ``regex`` and ``command``.

Here's an example of routing messages with the text ``@here`` or ``@channel``, to a built-in callback function, based on a regex match:

.. code-block:: yaml

   handlers:
     message_handlers:
       - match: ".*(@here|@channel).*"
         match_type: "regex"
         description: "Warn on @here or @channel."
         bots:
           "example-production":
             - "omnibot"
         callbacks:
           - module: "omnibot.callbacks.message_callbacks:specials_callback"
             kwargs:
               channels:
                 random:
                   message: "Please don't `{special}` as it notifies {member_count} people."
                   reaction: "broken_heart"

This handler has a regex that will match against any message with ``@here`` or ``@channel`` in the text that slack delivers to this bot, and will route it to the ``omnibot.callbacks.message_callbacks:specials_callback`` callback.

Here's another example, that will only respond to the ``docs`` command directed at a configured bot (e.g. ``@omnibot docs how do I configure handlers``):

.. code-block:: yaml

   handlers:
     message_handlers:
       - match: "docs"
         match_type: "command"
         description: "Find documentation relevant to this channel."
         bots:
           "example-production":
             - "omnibot"
         callbacks:
           - module: "omnibot.callbacks.network_callbacks:http_callback"
             kwargs:
               request_kwargs:
                 url: "https://docbot.local/api/v1/docbot/messages"

A single bot can have more than one command routed to it. Similarly, we can route commands to the same callback, but from different bots:

.. code-block:: yaml

   handlers:
     message_handlers:
       - match: "docs"
         match_type: "command"
         description: "Find documentation relevant to this channel."
         bots:
           "example-production":
             - "omnibot"
         callbacks:
           - module: "omnibot.callbacks.network_callbacks:http_callback"
             kwargs:
               request_kwargs:
                 url: "https://docbot.local/api/v1/docbot/messages"
       - match: ""
         match_type: "command"
         description: "Find documentation relevant to this channel."
         bots:
           "example-production":
             - "docbot"
         callbacks:
           - module: "omnibot.callbacks.network_callbacks:http_callback"
             kwargs:
               request_kwargs:
                 url: "https://docbot.local/api/v1/docbot/messages"

The empty string match above (``match: ""``) will send any message directed to the bot to the callback, without needing to match a particular command. So, the following two messages work identically::

    @omnibot docs api FAQ
    @docbot api FAQ

This makes it easy to migrate functionality from one bot to another, or to combine functionality from multiple bots into a single bot with little effort.

Matches are checked in order, and only the first match is used, which makes it possible to override subcommands from one handler with another:

.. code-block:: yaml

   handlers:
     message_handlers:
       - match: "override"
         match_type: "command"
         description: "Find documentation relevant to this channel."
         bots:
           "example-production":
             - "docbot"
         callbacks:
           - module: "omnibot.callbacks.network_callbacks:http_callback"
             kwargs:
               request_kwargs:
                 url: "https://overridebot.local/api/v1/overridebot/messages"
       - match: ""
         match_type: "command"
         description: "Find documentation relevant to this channel."
         bots:
           "example-production":
             - "docbot"
         callbacks:
           - module: "omnibot.callbacks.network_callbacks:http_callback"
             kwargs:
               request_kwargs:
                 url: "https://docbot.local/api/v1/docbot/messages"

The above will send ``@docbot override ...`` to ``https://overridebot.local/api/v1/overridebot/messages``, but will send any other ``@docbot ...`` command to ``https://docbot.local/api/v1/docbot/messages``.

Interactive Component Handlers
==============================

Interactive components map interactive component events from Slack (like a button click in an interactive message) to a list of bots in a particular team to callback functions. Interactive component handlers have the following options:

* ``callback_id``: The callback id to route for. Callback ids are generally set via dialogs, interactive messages, message actions, or other forms of slack interactive feature sets.
* ``response_type``: ``in_channel`` or ``ephemeral``. ``in_channel`` will display the callback response in the channel. ``ephemeral`` will display the response from the callback in the channel.
* ``bots``: A dict of slack teams, each team specifying a list of bots we accept these interactive commands from.
* ``dialog``: A dict configuring a dialog response to display when an interactive component is used. See the slack interactive dialog docs for configuration options here. Note that dialogs must specify a callback id that correlates with a configured interactive component handler.
* ``canned_response``: A response for omnibot to immediately respond with when the interactive component is received. This can be useful if the callback is slow or sometimes flaky, as it'll let you tell the end-user that the bot it working on it.
* ``no_message_response``: By default, upon responding to an interactive message component, omnibot will overwrite the message that a bot sends with another message. Either a "canned response" that you specify or the response type if the response type is "in_channel". Setting no_message_response to ``true`` prevents this from happening.
* ``callbacks``: A list of callbacks to route the interactive component to.

As an example, let's say that we want to add a message action, that will let a user submit a slack thread to a service, that will turn the slack thread into a stackoverflow question with a list of answers based on the thread and its responses:

.. code-block:: yaml

  handlers:
    interactive_component_handlers:
      - callback_id: "stackoverflow_thread_submit"
        response_type: "in_channel"
        canned_response: "Submitting thread..."
        bots:
          "example-production":
            - "omnibot"
        callbacks:
          - module: "omnibot.callbacks.network_callbacks:http_callback"
            kwargs:
              request_kwargs:
                url: "https://so-seeder.local/api/v1/interactive-component"

It's also possible to respond to an interactive component with a dialog, that will let you chain the handler with another handler:

.. code-block:: yaml

  handlers:
    interactive_component_handlers:
      - callback_id: "stackoverflow_thread_prompt"
        response_type: "in_channel"
        bots:
          "example-production":
            - "omnibot"
        dialog:
          title: "Thread submission"
          submit_label: "submit"
          callback_id: "stackoverflow_thread_submit"
          elements:
            - type: "checkbox"
              label: "Attribute answers to original authors"
              name: "attribution_element"
      - callback_id: "stackoverflow_thread_submit"
        response_type: "in_channel"
        canned_response: "Submitting thread..."
        bots:
          "example-production":
            - "omnibot"
        callbacks:
          - module: "omnibot.callbacks.network_callbacks:http_callback"
            kwargs:
              request_kwargs:
                url: "https://so-seeder.local/api/v1/interactive-component"

The above uses two chained together handlers. The first handler is what you'd point the message action at; omnibot will respond with the configured dialog, which points at the second handler. The second handler routes the dialog response to the configured callback. Note that the first handler doesn't have any callbacks set, because we're only using this to chain handlers together.

Slash Command Handlers
======================

Slash command handlers route slash commands from Slack to a list of bots in a particular team to callback functions. Slash command handlers have the following options:

* ``command``: The slash command to route for (defined in the slack API dashboard)
* ``response_type``: ``in_channel`` or ``ephemeral``. ``in_channel`` will display both the slash command used, as well as any response from the callback. ``ephemeral`` will only display the response from the callback.
* ``bots``: A dict of slack teams, each team specifying a list of bots we accept these slash commands from.
* ``dialog``: A dict configuring a dialog response to display when a slash command is used. See the slack interactive dialog docs for configuration options here. Note that dialogs must specify a callback id that correlates with a configured interactive component handler.
* ``canned_response``: A response for omnibot to immediately respond with when the slash command is received. This can be useful if the callback is slow or sometimes flaky, as it'll let you tell the end-user that the bot it working on it.
* ``no_message_response``: By default, upon responding to an slash command, omnibot will overwrite the message that a bot sends with another message. Either a "canned response" that you specify or the response type if the response type is "in_channel". Setting no_message_response to ``true`` prevents this from happening.
* ``callbacks``: A list of callbacks to route the slash commands to.

As an example, let's say we want to have a slash command ``/echo`` that will respond back with whatever text the end-user provided:

.. code-block:: yaml

  handlers:
    slash_command_handlers:
      - command: "/echo"
        response_type: "in_channel"
        bots:
          "example-production":
            - "omnibot"
        callbacks:
          - module: "omnibot.callbacks.slash_command_callbacks:echo_callback"

When an end-user uses ``/echo test``, the omnibot bot in Slack will respond with ``test``. Let's say for instance, that you wanted to take the text from a dialog, when ``/echo`` is used, rather than providing the text after the slash command:

.. code-block:: yaml

  handlers:
    slash_command_handlers:
      - command: "/echo"
        response_type: "in_channel"
        bots:
          "example-production":
            - "omnibot"
        dialog:
          title: "Echo dialog"
          submit_label: "submit"
          callback_id: "echo_submit"
          elements:
            - type: "text"
              label: "Echo this text"
              name: "echo_element"

In the above, there's no callbacks configured, as we're chaining a slash command handler with an interactive component handler. This handler configuration alone wouldn't do anything, without a correlated interactive component handler, which could be configured like so:

.. code-block:: yaml

  handlers:
    interactive_component_handlers:
      - callback_id: "echo_submit"
        response_type: "in_channel"
        bots:
          "example-production":
            - "omnibot"
        callbacks:
          - module: "omnibot.callbacks.interactive_component_callbacks:echo_dialog_submission_callback"

********************************
API Access Control Configuration
********************************

omnibot has a pluggable authorization system for its API. omnibot has both an external and an internal API; the external API is what Slack talks to, and the internal API is used by your services to talk to Slack. By default, for security purposes, omnibot is configure to deny all API calls if the authorization system isn't configured.

The following basic configuration is recommended for allowing Slack to call omnibot's external APIs, while disabling internal APIs:

.. code-block:: yaml

  authorization:
    checks:
      module: "omnibot.authnz:allowed_paths"
      kwargs:
        paths:
          - "/api/v1/slack/event"
          - "/api/v1/slack/slash_command"
          - "/api/v1/slack/interactive"

The above allows ``event subscriptions``, ``slash commands``, and ``interactive components`` to be sent to omnibot, from Slack.

Note that checks configured are additive: all configured checks must pass for a request to be allowed.

For specific configuration for available checks, see the documentation specific to each check. omnibot ships with the following checks available:

* :func:`omnibot.authnz.allowed_paths()`
* :func:`omnibot.authnz.envoy_checks.envoy_internal_check()`
* :func:`omnibot.authnz.envoy_checks.envoy_permissions_check()`
