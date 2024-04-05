#####################
Adding new slack apps
#####################

.. _adding-normal-slack-apps:

************************
Adding normal slack apps
************************

#. Visit the `slack api console <https://api.slack.com/apps>`_, click the ``Create New App`` button, add the app name (should match the bot name), and select the Slack Workspace
#. Add any necessary collaborators, using the ``Collaborators`` link in the sidebar. It's recommended to keep this list to the set of omnibot admins.
#. Add a bot user, using the ``Bot Users`` link in the sidebar. Add the display name and username (they should match, and should match the app name). Enable ``Always Show My Bot as Online``.
#. Add the necessary OAuth scopes, using the ``OAuth & Permissions`` link in the sidebar. The scopes necessary for the bot depend on the bot's usage, but a subset of scopes are recommended for every bot:

   * ``channels:history``
   * ``channels:read``
   * ``chat:write:bot``
   * ``chat:write:user``
   * ``groups:read``
   * ``im:read``
   * ``mpim:read``
   * ``files:read``
   * ``bot``
   * ``reactions:read``
   * ``reactions:write``
   * ``links:read``
   * ``links:write``
   * ``users:read``
   * ``users:read.email``

#. Install the app, using the ``Install App`` link in the sidebar. It's necessary to install this app at this point, so that we can get the credentials for the app.
#. Save the credentials for the application:

   #. From the ``OAuth & Permissions`` link in the sidebar, save the ``OAuth Access Token`` and ``Bot User OAuth Access Token`` values.
   #. From the ``Basic Information`` link in the sidebar, save the ``App ID`` and ``Verification Token`` values.

#. At this point you'll want to add the bot to the omnibot :doc:`configuration`, then restart the omnibot services. It's necessary for omnibot to be able to accept events from slack before proceeding.
#. Add event subscriptions (if the bot needs event subscriptions), using the ``Event Subscriptions`` link in the sidebar:

   #. Add the request URL. This will be the event API route; so, if your omnibot hostname is ``omnibot.example.com``, the URL would be ``https://omnibot.example.com/api/v1/slack/event``. Slack will verify the URL, and will only allow you to save if it's working.
   #. You'll need to decide whether or not a bot should receive workspace events. Workspace events will be sent to the app for any event of this type in the entire workspace, whether or not the bot is a part of the conversation, which likely means the only ``message`` event you'll want to put here is ``message.channels``, otherwise you'll unintentionally send private conversations to the bot. The recommended configuration for most bots is to add the following bot events:

      * message.channels
      * message.groups
      * message.im
      * message.mpim
   #.
      * Note 1: adding ``app_mention`` may result in your bot being called twice.
      * Note 2: the configuration `bot.name` for your bot should match your app user_handle
      * Note 3: if your app user_handle does not match your `bot.name` you need to
        specify `match_mention: true` to receive callbacks


#. Add interactive component configuration (if the bot needs interactive components), using the ``Interactive Components`` link in the sidebar:

   #. Add the request URL. This will be the interactibe API route; so, if your omnibot hostname is ``omnibot.example.com``, the URL would be ``https://omnibot.example.com/api/v1/slack/interactive``. Slack will not verify this URL, unfortunately.
   #. Add message actions (if the bot will provide message action functionality). The callback used here needs to match an interactive component handler in the omnibot configuration.
   #. (omnibot doesn't yet support message menus)

#. Add slash commands (if the bot needs slash commands), using the ``Slash Commands`` link in the sidebar:

   #. Set the command name (``/echo`` for instance)
   #. Set the request URL. This will be the slash_command API route; so, if your omnibot hostname is ``omnibot.example.com``, the URL would be ``https://omnibot.example.com/api/v1/slack/slash_command``. Slack will not verify this URL, unfortunately.
   #. Set the description.
   #. Set the usage hint.
   #. Ensure ``Escape channels, users, and links sent to your app`` is enabled.

.. _adding-primary-bot-slack-apps:

*******************************************
Adding a slack app for use as a primary bot
*******************************************

A primary bot is used by the watcher to poll certain APIs in slack for your team and to cache that data for use in parsing. Your primary bot needs a minimum set oauth permissions to correctly poll:

* OAuth scopes required:
   * ``channels:read``
   * ``groups:read``
   * ``im:read``
   * ``mpim:read``
   * ``files:read``
   * ``users:read``
   * ``users:read.email``
   * ``emoji:read``

Otherwise, setup instructions for a primary bot are the same as a normal bot. Note that your primary bot isn't limited to this function, and if you want to use it as a normal bot in your slack team, please do so.
