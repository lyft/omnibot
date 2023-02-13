from flask import Flask

from omnibot import settings

app = Flask(__name__)
app.config.from_object(settings)
