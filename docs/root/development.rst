##########################
Quickstart and Development
##########################

*************
Prerequisites
*************

#. You'll need a slack team (a slack workspace/account that omnibot will work within). You'll need to `find your team ID <https://stackoverflow.com/questions/40940327/what-is-the-simplest-way-to-find-a-slack-team-id-and-a-channel-id>`_.
#. You'll need :ref:`a slack app (bot) <adding-normal-slack-apps>` to connect to omnibot. You'll need the app's App ID, which is in the ``Basic Information`` section of the api dashboard.
#. You'll need the ``Verification Token`` (in the ``Basic Information`` section), and the ``OAuth Access Token`` and ``Bot User OAuth Access Token`` (both in the ``OAuth & Permissions`` section) for your slack app.
#. You'll need :ref:`a primary bot <adding-primary-bot-slack-apps>`, which the watcher worker will use to poll some APIs in slack and cache their information. Omnibot's cache is relatively critical to its operations, so you need a primary bot.
#. You don't necessarily need to be an admin in the slack team, but it'll help. If you don't have slack admin, you'll need an admin to install your slack apps for you, and they may need to provide you with the oauth token.

.. _quickstart:

**********
Quickstart
**********

This quickstart will start omnibot, connect a slack app to omnibot, and have a very basic handler respond to messages.

Add basic omnibot configuration:

``config/development/omnibot.env``:

.. code-block:: bash

    # A87654321 here is an example, and should be replaced with the app id for your slack app/bot
    CREDENTIALS_SLACK_OAUTH_BOT_TOKEN_A87654321=xoxb-...
    CREDENTIALS_SLACK_OAUTH_TOKEN_A87654321=xoxp-...
    CREDENTIALS_SLACK_VERIFICATION_TOKEN_A87654321=...
    # For development via docker-compose, any region is fine, since we're using fake AWS services
    AWS_DEFAULT_REGION=us-east-1
    # AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are not required, if this is accessible from a
    # metadata service (like metadataproxy). Without a metadata service, you need to add some
    # fake credentials here, or the fake AWS services will complain
    AWS_ACCESS_KEY_ID=1
    AWS_SECRET_ACCESS_KEY=1
    # LOG_CONFIG_FILE isn't required, but watcher and webhook workers will have minimum and
    # unformatted log output otherwise
    LOG_CONFIG_FILE=/etc/omnibot/logging.yaml
    # Redis and SQS settings to match what's in the docker-compose setup
    REDIS_HOST=redis
    REDIS_PORT=6379
    SQS_QUEUE_NAME=omnibot
    SQS_URL=http://sqs:9203

``config/development/omnibot.conf``:

.. code-block:: yaml

   # The basic authorization block required to accept events from slack
   authorization:
     checks:
       - module: "omnibot.authnz:allowed_paths"
         kwargs:
           paths:
             - "/api/v1/slack/event"
             - "/api/v1/slack/slash_command"
             - "/api/v1/slack/interactive"
   # A friendly name to associate with your team, and its team ID
   # The friendly name is used in API endpoints you may make accessible
   teams:
     "friendly-name-for-your-team": "T12345678"
   # The dict of bots associated with your team. The friendly name for your bot is used
   # to reference the bot in the config, and also in API endpoints you may make accessible.
   bots:
     "friendly-name-for-your-team":
       "your-slack-app-name": "A87654321"
   # The bot that omnibot proxy will use to poll slack for user, channel, etc. info
   primary_bot:
     "friendly-name-for-your-team": "your-slack-app-name"
   # Event handlers, for routing incoming slack events to callback functions
   handlers:
     message_handlers:
       # A command handler that matches any command sent to your-slack-app-name, in
       # friendly-name-for-your-team and sends it to a test_handler.
       - match: ""
         match_type: "command"
         description: "testing"
         bots:
           "friendly-name-for-your-team"
              - "your-slack-app-name"
         callbacks:
           - module: "omnibot.callbacks.message_callbacks:test_callback"
             kwargs:
               text: 'test'

Start omnibot, using docker-compose:

.. code-block:: bash

   cd <path-to-omnibot-repo>
   docker-compose up

Note that it's normal to see some errors on startup from docker compose about missing SQS queues or boto connection refused while things are starting up. Until local SQS starts up, dependent services fail and restart. Eventually, you should see a poll loop with output like the following: ``omnibot-webhook_1       | {"asctime": "2019-08-30 19:02:01,295", "name": "__main__", "levelname": "DEBUG", "message": "No messages, continuing"}``

Start `ngrok <https://ngrok.com/download>`_:

.. code-block:: bash

   /<path-to-ngrok-binary>/ngrok http 80

Connect your slack app's ``Event Subscriptions`` to the https ngrok link (see the `Forwarding` section of the ngrok command output), using the ``Event Subscriptions`` section of the slack api dashboard. Example URL: ``https://abcd.ngrok.com/api/v1/slack/event``

You should likely add the following event subscriptions:

* Bot Events

  * ``message.channels``
  * ``message.groups``
  * ``message.im``
  * ``message.mpim``

Invite your app into a channel in your slack workspace, and send any message to it: ``@your-slack-app-name hello``

The app should respond back with ``test`` in a thread.

Developing new bots
===================

The recommended way to develop bots using omnibot is to match events using handlers, and to configure those handlers to forward events to your own backend services using the http network callback in the callbacks. This generally requires only configuration changes in omnibot, unless the omnibot proxy doesn't currently have support for the slack feature you need to use. See the :ref:`handler configuration <handler_configuration>` for common ways to match and forward events to your own services.

It's possible to add a callback module directly to omnibot, using it as a framework, rather than as a proxy, but you should likely use the http callback if any of these conditions are true:

* If you need to add a new pip requirement to omnibot (this may cause you to have conflicts in dependency requirements, or may change a library to an incompatible version)
* If you need to make a large number of external API calls (this will cause concurrency issues as it'll hold your request in the thread pool longer)
* If you need to use a lot of CPU (this will cause concurrency issues, as your callback won't yield)
* If you need to store data

Basically, you want to avoid one callback causing issues for the rest of omnibot's bots and callbacks. Isolating your bot's code in a new service ensures you're isolating the operations and availability of your bot as well.

Making and testing changes to omnibot using docker and docker-compose
=====================================================================

If you want to develop against omnibot itself, the recommended approach is to use docker and docker-compose. The standard process is:

#. docker-compose up
#. Make changes
#. docker build -t lyft/omnibot .
#. docker-compose restart
#. <repeat>
