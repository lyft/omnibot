<p align="center">
  <img src="docs/root/_static/logo.png?raw=true">
</p>

# omnibot

omnibot is a Slack proxy that can route Slack events to various ``handlers``. ``handlers`` match different types of Slack events and send them to callbacks, which are pluggable python modules. For the most part, all you need to do is to configure omnibot to route messages via your handlers, and return a list of actions for omnibot to take on a bot's behalf.

## Docs

For more detailed information, please see [the docs](https://lyft.github.io/omnibot).
