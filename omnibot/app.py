from __future__ import absolute_import

from flask import Flask

from omnibot import settings

app = Flask(__name__)
app.config.from_object(settings)
