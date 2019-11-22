############
Installation
############

**********************
Quickstart for testing
**********************

If you just want to checkout omnibot and aren't looking to deploy it into
production check out the :ref:`quickstart <quickstart>`.

*******************
Docker installation
*******************

To run omnibot in Docker
========================

omnibot is configured through a combination of environment variables and a configuration
file. When starting the docker container, you'll need to inject both, which can be done
via ``--env-file`` and ``-v`` arguments.

.. code-block:: bash

    docker pull lyft/omnibot
    # You can also override the logging config, via: -v logging.conf:/etc/omnibot/logging.conf
    docker run --env-file omnibot.env -v omnibot.conf:/etc/omnibot/omnibot.conf -t lyft/omnibot -c "gunicorn --config /srv/omnibot/config/gunicorn.conf omnibot.wsgi:app --workers=2 -k gevent --access-logfile=- --error-logfile=-"
    docker run --env-file omnibot.env -v omnibot.conf:/etc/omnibot/omnibot.conf -t lyft/omnibot -c "python3 -m omnibot.webhook_worker"
    docker run --env-file omnibot.env -v omnibot.conf:/etc/omnibot/omnibot.conf -t lyft/omnibot -c "python3 -m omnibot.watcher"

To build the image
==================

If you want to build the image and store it in your private registry, you can
do the following:

.. code-block:: bash

    git clone https://github.com/lyft/omnibot
    cd omnibot
    docker build -t lyft/omnibot .

****************
pip installation
****************

#. Using Ubuntu or Debian (please help with non-Ubuntu/Debian install
   instructions!)
#. venv location: /srv/omnibot/venv

Make a virtualenv and install pip requirements
==============================================

.. code-block:: bash

    sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv openssl libssl-dev gcc pkg-config libffi-dev libxml2-dev libxmlsec1-dev
    cd /srv/omnibot
    virtualenv3 venv
    source venv/bin/activate
    pip3 install -U pip
    pip3 install omnibot
    deactivate

*******************
Manual installation
*******************

Assumptions:

#. Using Ubuntu or Debian (please help with non-Ubuntu/Debian install
   instructions!)
#. Installation location: /srv/omnibot/venv
#. venv location: /srv/omnibot/venv

Clone omnibot
=============

.. code-block:: bash

    cd /srv
    git clone https://github.com/lyft/omnibot

Make a virtualenv and install pip requirements
==============================================

.. code-block:: bash

    sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv openssl libssl-dev gcc pkg-config libffi-dev libxml2-dev libxmlsec1-dev
    cd /srv/omnibot
    virtualenv venv
    source venv/bin/activate
    pip install -U pip
    pip install -r piptools_requirements3.txt
    pip install -r requirements3.txt
    deactivate

Run omnibot
===========

It's necessary to export your configuration variables before running omnibot.
The easiest method is to source a file that exports your environment before
running omnibot. You'll also need to write a configuration file to /etc/omnibot/omnibot.conf
(or to a location of your choosing, via the ``CONFIG_FILE`` environment variable).

.. code-block:: bash

    mkdir /etc/omnibot
    mkdir /var/log/omnibot
    cd /srv/omnibot
    # You need to create omnibot.env, and omnibot.conf
    cp omnibot.env /etc/omnibot/
    source /etc/omnibot/omnibot.env
    cp omnibot.conf /etc/omnibot/
    # A default logging config is included
    cp conf/logging.conf /etc/omnibot/
    source venv/bin/activate
    # You should really probably use some form of an init system here, rather than running them directly.
    gunicorn --config /srv/omnibot/config/gunicorn.conf omnibot.wsgi:app --workers=2 -k gevent --access-logfile=/var/log/omnibot/omnibot.log --error-logfile=/var/log/omnibot/omnibot.err &
    python3 -m omnibot.webhook_worker > /var/log/omnibot/webhook_worker.log &
    python3 -m omnibot.watcher > /var/log/omnibot/watcher.log &
