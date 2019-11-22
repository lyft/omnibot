from __future__ import absolute_import

from omnibot.app import app
from omnibot import settings

from omnibot.routes import api
app.register_blueprint(api.blueprint)


if __name__ == '__main__':
    from omnibot import setup_logging  # noqa:F401
    app.run(
        host=settings.get('HOST', '0.0.0.0'),
        port=settings.get('PORT', 5000),
        debug=settings.get('DEBUG', True))
