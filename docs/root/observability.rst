.. _observability:

#############
Observability
#############

omnibot is a distributed system, and as such observability is important. Observability through omnibot is primarily handled through stats and logs.

.. _observability_stats:

*****
Stats
*****

Delivery and Processing
=======================

Stats related to delivery and processing of event subscription, slash command, and interactive component events. These stats can help you determine whether slack or omnibot is at fault for latency or failures:

.. csv-table::
  :header: Name, Type, Description
  :widths: 1, 1, 2

  pre_sqs_delivery_latency, Timer, "Latency of event subscription events between occurance and delivery from slack to omnibot API"
  pre_sqs_delivery_retry_latency, Timer, "Latency of event subscription events between occurance and delivery from slack to omnibot API, for events being retried"
  delivery_latency, Timer, "Post-SQS delivery latency of event subscription events between occurance and omnibot's webhook worker receiving it from SQS"
  sqs.sent, Counter, "Number of SQS messages enqueued"
  sqs.<bot_name>.sent, Counter, "Number of SQS messages enqueued for the specific configured bot"
  sqs.received, Counter, "Number of SQS messages dequeued"
  handle_message, Timer, "Post-SQS processing latency of SQS messages, including message JSON deserialization, end-to-end handler and callback processing, and SQS message deletion"
  process_event, Timer, "Post-SQS processing latency of slack event subscription events, including end-to-end handler and callback processing"
  event.process.attempt.<event_type>, Counter, "Number of times omnibot received an event subscription event and attempted to process it"
  event.process.failed.<event_type>, Counter, "Number of times omnibot received an event subscription event and failed to process it"
  event.handled, Counter, "Number of times a processed event subscription event matched a configured handler"
  event.defaulted, Counter, "Number of times a processed event subscription event defaulted to a help handler"
  event.ignored, Counter, "Number of times a processed event subscription event did not match any handler and was ignored"
  event.unsupported, Counter, "Number of times a processed event subscription event wasn't of a supported type and was ignored"
  process_slash_command, Timer, "Post-SQS processing latency of slack slash command events, including end-to-end handler and callback processing"
  slash_command.process.attempt.<command_name>, Counter, "Number of times omnibot received a slash command event and attempted to process it"
  slash_command.process.failed.<command_name>, Counter, "Number of times omnibot received a slash command event and failed to process it"
  process_interactive_component, Timer, "Post-SQS processing latency of slack interactive component events, including end-to-end handler and callback processing"
  interactive_component.process.attempt.<component>, Counter, "Number of times omnibot received an interactive component event and attempted to process it"
  interactive_component.process.failed.<component>, Counter, "Number of times omnibot received an interactive component event and failed to process it"
  unexpand_metadata, Timer, "Parsing latency of specials, channels, and users when defined in omnibot_parse of handler responses"
  parser.extract_users, Timer, "Parsing latency for converting from slack format to friendly format for users"
  parser.extract_channels, Timer, "Parsing latency for converting from slack format to friendly format for users"
  parser.extract_subteams, Timer, "Parsing latency for converting from slack format to friendly format for subteams"
  parser.extract_specials, Timer, "Parsing latency for converting from slack format to friendly format for specials"
  parser.extract_emojis, Timer, "Parsing latency for converting from slack format to friendly format for emojis"
  parser.extract_emails, Timer, "Parsing latency for converting from slack format to friendly format for emails"
  parser.extract_urls, Timer, "Parsing latency for converting from slack format to friendly format for urls"
  parser.extract_mentions, Timer, "Parsing latency for converting from slack format to friendly format for mentions"
  parser.extract_command, Timer, "Parsing latency for converting from slack format to friendly format for commands"
  parser.unextract_specials, Timer, "Parsing latency for converting from friendly format to slack format for specials"
  parser.unextract_channels, Timer, "Parsing latency for converting from friendly format to slack format for channels"
  parser.unextract_users, Timer, "Parsing latency for converting from friendly format to slack format for users"

When considering dashboards, a few useful things:

* If pre_sqs_delivery_latency is >10-15s, it's likely that slask is having an outage
* If pre_sqs_delivery_latency is <10-15s and delivery_latency is drastically higher than pre_sqs_delivery_latency, then omnibot is spending a large amount of time processing messages, and you should look at other processing and delivery metrics, like sqs, parser.\*, and process\*
* If any of the parser metrics are very slow, it's likely you're having issues with redis, as the parser functions will fallback to slack if caches are missing
* If sqs.sent and sqs.received don't match, you're likely having SQS issues
* If you're seeing \*.process.failed counts, then handlers are failing, and you can track that down using the logs

Webhook Worker Gevent Pool
==========================

Stats related to gevent pool latency. These stats can help you determine if you need to increase worker concurrency, or increase the number of workers running:

.. csv-table::
  :header: Name, Type, Description
  :widths: 1, 1, 2

  webhookpool.spawn, Timer, "Amount of time it takes to spawn a gevent thread into the webhookpool"
  webhookpool.pool.full, Counter, "Number of times the webhook worker has reached its maximum concurrency limit"

In general, if you're seeing full counts, you need more concurrency, or you need more worker processes running.


Watcher Worker Latency
======================

.. csv-table::
  :header: Name, Type, Description
  :widths: 1, 1, 2

  watch.users, Timer, "Latency per-run of watch_users, to fetch all user information for all teams and primary bots configured"
  watch.channels, Timer, "Latency per-run of watch_channels, to fetch all channel information for all teams and primary bots configured"
  watch.groups, Timer, "Latency per-run of watch_groups, to fetch all private group information for all teams and primary bots configured"
  watch.ims, Timer, "Latency per-run of watch_ims, to fetch all im channel information for all teams and primary bots configured"
  watch.mpims, Timer, "Latency per-run of watch_mpims, to fetch all mpim channel information for all teams and primary bots configured"
  watch.emoji, Timer, "Latency per-run of watch_emoji, to fetch all emoi information for all teams and primary bots configured"

If you're seeing issues with unparsed messages, or seeing high latency in parsing, these stats can help show how long it's taking to refresh the cache via the poll looping.

.. _observability_logs:

****
Logs
****

omnibot includes a logging configuration yaml file that can be used to ensure logs are JSON structured, and a number of the log messages include extra data that will help you trace logs back to specific event ids, event types, slack app ids, slack team ids, and specific friendly bot names. This data is passed through into handler callback functions. This allows you to track logs for particular events from delivery, to processing, into the handler, and back from the response from the callbacks, including cross-service, as long as the service called by the http handler logs the same infomation.

Event Subscription Tracing Data
===============================

.. csv-table::
  :header: Name, Description
  :widths: 1, 2

  event_ts, "The ID of the event subscription event from slack. In the case of slack messages, this is also the message ID."
  event_type, "The subtype of the event subscription event"
  app_id, "The ID of the slack app"
  team_id, "The ID of the slack workspace"
  bot_receiver, "The bot (friendly name) configured in omnibot that's associated with the app_id"

Slash Command Tracing Data
==========================

.. csv-table::
  :header: Name, Description
  :widths: 1, 2

  trigger_id, "The ID of the slash command event from slack."
  command, "The command name configured in the slack API for this slash command event."
  app_id, "The ID of the slack app"
  team_id, "The ID of the slack workspace"
  bot_receiver, "The bot (friendly name) configured in omnibot that's associated with the app_id"

Interactive Component Tracing Data
==================================

.. csv-table::
  :header: Name, Description
  :widths: 1, 2

  callback_id, "The callback id of the interactive component event from slack."
  component_type, "The type of interactive component event associated with the interactive component event from slack."
  app_id, "The ID of the slack app"
  team_id, "The ID of the slack workspace"
  bot_receiver, "The bot (friendly name) configured in omnibot that's associated with the app_id"
