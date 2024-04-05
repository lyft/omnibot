FROM ubuntu:bionic
LABEL maintainer="rlane@lyft.com"

COPY ./piptools_requirements.txt /srv/omnibot/piptools_requirements.txt
COPY ./requirements.txt /srv/omnibot/requirements.txt

WORKDIR /srv/omnibot

ENV PATH=/venv/bin:$PATH
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-dev python3-pip openssl libssl-dev gcc pkg-config libffi-dev libxml2-dev libxmlsec1-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install -r piptools_requirements.txt && \
    pip3 install -r requirements.txt

COPY . /srv/omnibot
