# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM debian:12
# If upgrading the version number from 12 to the next debian release, make sure to do the same
# also in the shell scripts stored in this directory.
MAINTAINER Francesco Ballarin <francesco.ballarin@unicatt.it>

ARG DJANGO_SECRET_KEY
ARG POSTGRES_PASSWORD

WORKDIR /root

RUN apt update -y -q && \
    apt install -y -qq curl net-tools python3-pip sudo unzip vim wget

# Part 1: turing and its runtime dependencies
COPY patches patches
COPY turing turing

RUN apt install -y -qq postgresql postgresql-client postgresql-contrib && \
    echo "$POSTGRES_PASSWORD\n$POSTGRES_PASSWORD" | passwd postgres

RUN bash patches/turing/apply_patches.sh && \
    python3 -m pip install --break-system-packages -r turing/requirements.txt

RUN cat <<EOF > /root/turing/Turing/settings.ini
[settings]
SECRET_KEY=$DJANGO_SECRET_KEY
DEBUG=False
DEV_MODE=False
ALLOWED_HOSTS=*
INTERNAL_IPS=127.0.0.1
RDS_DB_NAME=turing-dmf-db
RDS_USERNAME=postgres
RDS_PASSWORD=$POSTGRES_PASSWORD
RDS_HOSTNAME=localhost
EOF

RUN cd turing && \
    python3 manage.py collectstatic

# Part 2: turing and its test dependencies
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt update -y -q && \
    apt install -y -qq google-chrome-stable

RUN LATEST_STABLE_RELEASE=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    CHROME_BASE_URL=https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$LATEST_STABLE_RELEASE && \
    wget -O /tmp/chromedriver.zip $CHROME_BASE_URL/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    rm -rf /tmp/chrome*

RUN python3 -m pip install --break-system-packages -r turing/requirements-dev.txt

# Part 3: mathrace-interaction
COPY mathrace_interaction mathrace_interaction

# Part 4: set up entrypoint that:
# * creates and initialize databases on first run,
# * starts the server
COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
