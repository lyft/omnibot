#############
Event parsing
#############

When omnibot receives events, it sanitizes the event (to remove sensitive info, like validation token), and injects extra metadata into the event, like parsed versions of some fields (like user, message, etc). This document can be used as a reference for how omnibot parses events.

*************************
Event Subscription Events
*************************

Currently, for event subscription events, omnibot only has direct support for message events (message.channels, message.groups, message.im, message.mpim).

Message Events
==============

When a message is sent to a channel, slack will provide a bot with everything in its special message format, which doesn't look anything at all like what you'd see in the channel. For example, here's what a message looks like in a channel::

    @rlane hey, come join me in #general, see https://github.com/lyft/omnibot for why

Here's what slack sends you::

    <@U6J3LTKSQ> hey, come join me in <#C4VQ6NUNN>, see <https://github.com/lyft/omnibot> for why

To see the original, you'd normally need to parse this back into the original, needing to make slack api calls for finding channels, users, etc. omnibot handles this for you. It'll parse the message, and turn this into a payload that'll get sent to your handler:

.. code-block:: json

    {
      "bot": "omnibot",
      "args": null,
      "text": "<@U6J3LTKSQ> hey, come join me in <#C4VQ6NUNN|general>, see <https://github.com/lyft/omnibot> for why",
      "parsed_text": "@omnibot hey, come join me in #general, see https://github.com/lyft/omnibot for why",
      "user": "U6J3LTKSQ",
      "parsed_user": {
        "id": "U6J3LTKSQ",
        "team_id": "T12345967",
        "name": "rlane",
        "deleted": false,
        "color": "3c989f",
        "real_name": "Ryan Lane",
        "tz": "America/Los_Angeles",
        "tz_label": "Pacific Standard Time",
        "tz_offset": -28800,
        "profile": {
          "first_name": "Ryan",
          "last_name": "Lane",
          "avatar_hash": "g04939292775",
          "title": "",
          "real_name": "Ryan Lane",
          "display_name": "rlane",
          "real_name_normalized": "Ryan Lane",
          "display_name_normalized": "rlane",
          "email": "rlane@lyft.com",
          "image_24": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=24&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0009-24.png",
          "image_32": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=32&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0009-32.png",
          "image_48": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=48&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0009-48.png",
          "image_72": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=72&d=https%3A%2F%2Fa.slack-edge.com%2F66f9%2Fimg%2Favatars%2Fava_0009-72.png",
          "image_192": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=192&d=https%3A%2F%2Fa.slack-edge.com%2F7fa9%2Fimg%2Favatars%2Fava_0009-192.png",
          "image_512": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2F7fa9%2Fimg%2Favatars%2Fava_0009-512.png",
          "team": "T12345967"
        },
        "is_admin": false,
        "is_owner": false,
        "is_primary_owner": false,
        "is_restricted": false,
        "is_ultra_restricted": false,
        "is_bot": false,
        "updated": 1504862981,
        "is_app_user": false,
        "has_2fa": false
      },
      "users": {
        "<@U6J3LTKSQ>": "rlane"
      },
      "channels": {
        "<#C4VQ6NUNN|general>": "general"
      },
      "subteams": {},
      "specials": {},
      "emojis": {},
      "emails": {},
      "urls": {
        "<https://github.com/lyft/omnibot>": "https://github.com/lyft/omnibot"
      },
      "channel_id": "C4VQ6NUNN",
      "channel": {
        "id": "C4VQ6NUNN",
        "name": "general",
        "is_channel": true,
        "created": 1491515285,
        "creator": "U4WF56QGP",
        "is_archived": false,
        "is_general": true,
        "unlinked": 0,
        "name_normalized": "general",
        "is_shared": false,
        "is_org_shared": false,
        "is_member": false,
        "is_private": false,
        "is_mpim": false,
        "members": [
          "U4WF56QGP",
          "U6HQQ19EC",
          "U6J3LTKSQ",
          "U6J4EGP44",
          "U6JDF1JBU",
          "U6JEGTFDZ",
          "U6JERPMJ7",
          "U6JG691MJ",
          "U6JGEQ0J0",
          "U6SAVUK44",
          "U750C7B37",
          "U7DH0H802"
        ],
        "topic": {
          "value": "test123",
          "creator": "U6J3LTKSQ",
          "last_set": 1507156612
        },
        "purpose": {
          "value": "This channel is for team-wide communication and announcements. All team members are in this channel.",
          "creator": "",
          "last_set": 0
        },
        "previous_names": [],
        "num_members": 9
      },
      "directed": true,
      "ts": "1507683858.000290"
    }

It'll auto-parse all of slack's markup, and in the payload it'll give you the parsed and unparsed versions of all the data, along with each type split into its own attribute, in case you want to quickly access any of the parsed data, or if you want to partially reparse the data yourself.

****************************
Interactive Component Events
****************************

Interactive component events occur when a user interacts with a various interactive component, like an interactive message, or a message actions. An example below is a user clicking the unregister button on an eventbot event in slack. When omnibot receives an event like this, it will inject some extra metadata to help downstream callbacks with common actions, like getting user info from a user id, or channel info from a channel id (``parsed_user`` and ``parsed_channel``). If a message is included with the interactive component event, omnibot will parse that message like a message event above.

.. code-block:: json

    {
        "omnibot_payload_type": "interactive_component",
        "bot": {
            "name": "your-slack-app-name",
            "bot_id": "A87654321"
        },
        "team": {
            "name": "friendly-name-for-your-team",
            "team_id": "T12345678"
        },
        "type": "interactive_message",
        "callback_id": "eventbot_events",
        "action_ts": "1566941256.572612",
        "message_ts": "1566417920.003500",
        "trigger_id": "728814876339.165116859648.9a3bcfc1b0bacf60542865403ea81002",
        "response_url": "https://hooks.slack.com/actions/T12345678/1231231234/hasdfigasf97g9asfgsadgf9",
        "original_message": {
            "type": "message",
            "subtype": "bot_message",
            "text": "Test evenbot event",
            "ts": "1566417920.003500",
            "username": "your-slack-app-name",
            "bot_id": "B87654321",
            "attachments": [
                {
                    "callback_id": "eventbot_events",
                    "id": 1,
                    "fields": [
                        {
                            "title": "Description",
                            "value": "hello world",
                            "short": false
                        },
                        {
                            "title": "Total attendees",
                            "value": "2",
                            "short": false
                        },
                        {
                            "title": "Attendee Venmo handles",
                            "value": "test_venmo_handle",
                            "short": false
                        },
                        {
                            "title": "Attendees missing Venmo handle",
                            "value": "None",
                            "short": false
                        },
                        {
                            "title": "Cost",
                            "value": "Total cost: $100.51; Cost per attendee: $50.26",
                            "short": false
                        },
                        {
                            "title": "Extra attendees",
                            "value": "1",
                            "short": false
                        }
                    ],
                    "actions": [
                        {
                            "id": "1",
                            "name": "update",
                            "text": "Update event details",
                            "type": "button",
                            "value": "1566417920.003500",
                            "style": ""
                        },
                        {
                            "id": "2",
                            "name": "refresh",
                            "text": "Refresh event details",
                            "type": "button",
                            "value": "1566417920.003500",
                            "style": ""
                        }
                    ],
                    "fallback": "[no preview available]"
                },
                {
                    "callback_id": "eventbot_events",
                    "title": "Manage your registration",
                    "id": 2,
                    "actions": [
                        {
                            "id": "3",
                            "name": "register",
                            "text": "Register",
                            "type": "button",
                            "value": "1566417920.003500",
                            "style": ""
                        },
                        {
                            "id": "4",
                            "name": "unregister",
                            "text": "Unregister",
                            "type": "button",
                            "value": "1566417920.003500",
                            "style": ""
                        },
                        {
                            "id": "5",
                            "name": "update_venmo",
                            "text": "Update Venmo",
                            "type": "button",
                            "value": "1566417920.003500",
                            "style": ""
                        }
                    ],
                    "fallback": "Manage your registration"
                }
            ]
        },
        "state": null,
        "user": {
            "id": "U6J3LTKSQ",
            "name": "rlane"
        },
        "parsed_user": {
            "id": "U6J3LTKSQ",
            "team_id": "T12345678",
            "name": "rlane",
            "deleted": false,
            "color": "3c989f",
            "real_name": "Ryan Lane",
            "tz": "America/Los_Angeles",
            "tz_label": "Pacific Daylight Time",
            "tz_offset": -25200,
            "profile": {
                "title": "",
                "phone": "",
                "skype": "",
                "real_name": "Ryan Lane",
                "real_name_normalized": "Ryan Lane",
                "display_name": "rlane",
                "display_name_normalized": "rlane",
                "status_text": "",
                "status_emoji": "",
                "status_expiration": 0,
                "avatar_hash": "g04939292775",
                "email": "rlane@lyft.com",
                "first_name": "Ryan",
                "last_name": "Lane",
                "image_24": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=24&d=https%3A%2F%2Fa.slack-edge.com%2F00b63%2Fimg%2Favatars%2Fava_0009-24.png",
                "image_32": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=32&d=https%3A%2F%2Fa.slack-edge.com%2F00b63%2Fimg%2Favatars%2Fava_0009-32.png",
                "image_48": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=48&d=https%3A%2F%2Fa.slack-edge.com%2F00b63%2Fimg%2Favatars%2Fava_0009-48.png",
                "image_72": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=72&d=https%3A%2F%2Fa.slack-edge.com%2F00b63%2Fimg%2Favatars%2Fava_0009-72.png",
                "image_192": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=192&d=https%3A%2F%2Fa.slack-edge.com%2F00b63%2Fimg%2Favatars%2Fava_0009-192.png",
                "image_512": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2F00b63%2Fimg%2Favatars%2Fava_0009-512.png",
                "status_text_canonical": "",
                "team": "T12345678"
            },
            "is_admin": true,
            "is_owner": true,
            "is_primary_owner": true,
            "is_restricted": false,
            "is_ultra_restricted": false,
            "is_bot": false,
            "is_app_user": false,
            "updated": 1525293976
        },
        "channel": {
            "id": "C6KD0QX0Q",
            "name": "test-omnibot"
        },
        "parsed_channel": {
            "id": "C6KD0QX0Q",
            "name": "test-omnibot",
            "is_channel": true,
            "created": 1502257073,
            "is_archived": false,
            "is_general": false,
            "unlinked": 0,
            "creator": "U6J3LTKSQ",
            "name_normalized": "test-omnibot",
            "is_shared": false,
            "is_org_shared": false,
            "is_member": true,
            "is_private": false,
            "is_mpim": false,
            "topic": {
                "value": "test",
                "creator": "U6J3LTKSQ",
                "last_set": 1515793069
            },
            "purpose": {
                "value": "",
                "creator": "",
                "last_set": 0
            },
            "previous_names": [],
            "num_members": 12
        },
        "message": null,
        "submission": null,
        "actions": [
            {
                "name": "unregister",
                "type": "button",
                "value": "1566417920.003500"
            }
        ]
    }

********************
Slash Command Events
********************

Slash command events occur when a user invokes a slash command that points at omnibot (e.g. ``/tableflip``).  An example below is a user clicking the unregister button on an eventbot event in slack. When omnibot receives an event like this, it will inject some extra metadata to help downstream callbacks with common actions, like getting user info from a user id, or channel info from a channel id (``parsed_user`` and ``parsed_channel``). If a message is included with the interactive component event, omnibot will parse that message like a message event above.

.. code-block:: json

    {
      "omnibot_payload_type": "slash_command",
      "bot": {
        "name": "your-slack-app-name",
        "bot_id": "A87654321"
      },
      "team": {
        "name": "friendly-name-for-your-team",
        "team_id": "T12345678"
      },
      "enterprise_id": null,
      "enterprise_name": null,
      "command": "/tableflip",
      "response_url": "https://hooks.slack.com/actions/T12345678/1231231234/hasdfigasf97g9asfgsadgf9",
      "trigger_id": "795200246613.165116859648.9500e32e47f5c1f2f2fc57a6014d92e6",
      "user_id": "U6J3LTKSQ",
      "parsed_user": {
        "id": "U6J3LTKSQ",
        "team_id": "T12345678",
        "name": "rlane",
        "deleted": false,
        "color": "3c989f",
        "real_name": "Ryan Lane",
        "tz": "America/Los_Angeles",
        "tz_label": "Pacific Daylight Time",
        "tz_offset": -25200,
        "profile": {
          "title": "",
          "phone": "",
          "skype": "",
          "real_name": "Ryan Lane",
          "real_name_normalized": "Ryan Lane",
          "display_name": "rlane",
          "display_name_normalized": "rlane",
          "status_text": "",
          "status_emoji": "",
          "status_expiration": 0,
          "avatar_hash": "g4939292775a",
          "email": "rlane@lyft.com",
          "first_name": "Ryan",
          "last_name": "Lane",
          "image_24": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=24&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-24.png",
          "image_32": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=32&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-32.png",
          "image_48": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=48&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-48.png",
          "image_72": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=72&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-72.png",
          "image_192": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=192&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-192.png",
          "image_512": "https://secure.gravatar.com/avatar/04939292775a6f4a1817e5e846c11609.jpg?s=512&d=https%3A%2F%2Fa.slack-edge.com%2Fdf10d%2Fimg%2Favatars%2Fava_0009-512.png",
          "status_text_canonical": "",
          "team": "T12345678"
        },
        "is_admin": true,
        "is_owner": true,
        "is_primary_owner": true,
        "is_restricted": false,
        "is_ultra_restricted": false,
        "is_bot": false,
        "is_app_user": false,
        "updated": 1569022884
      },
      "text": "",
      "parsed_text": "",
      "channel_id": "C6KD0QX0Q",
      "channel": {
        "id": "C6KD0QX0Q",
        "name": "test-omnibot",
        "is_channel": true,
        "created": 1502257073,
        "is_archived": false,
        "is_general": false,
        "unlinked": 0,
        "creator": "U6J3LTKSQ",
        "name_normalized": "test-omnibot",
        "is_shared": false,
        "is_org_shared": false,
        "is_member": true,
        "is_private": false,
        "is_mpim": false,
        "topic": {
          "value": "test",
          "creator": "U6J3LTKSQ",
          "last_set": 1515793069
        },
        "purpose": {
          "value": "",
          "creator": "",
          "last_set": 0
        },
        "previous_names": [],
        "num_members": 11
      },
      "users": {},
      "channels": {},
      "subteams": {},
      "specials": {},
      "emojis": {},
      "emails": {},
      "urls": {}
    }
