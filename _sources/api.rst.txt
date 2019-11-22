###
API
###

Omnibot has a set of APIs that can be used to get information from slack, or to allow other services to act on behalf of a slack app for a specified workspace. See the API docs for more detailed information.

By default the API disallows access to all routes. Please see the :doc:`configuration` docs for how to manage access control for the API.

***********************
API route documentation
***********************

.. qrefflask:: omnibot.wsgi:app
   :endpoints:
   :undoc-static:
   :undoc-endpoints: api.healthcheck, api.slack_event

.. autoflask:: omnibot.wsgi:app
   :endpoints:
   :undoc-static:
   :undoc-endpoints: api.healthcheck, api.slack_event
