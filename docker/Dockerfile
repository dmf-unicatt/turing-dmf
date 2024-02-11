# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM debian:12
MAINTAINER Francesco Ballarin <francesco.ballarin@unicatt.it>

WORKDIR /root

RUN apt update -y -q && \
    apt install -y -qq curl net-tools python3-pip vim wget

# Part 1: turing and its runtime dependencies
COPY turing turing
COPY patches patches

RUN bash patches/turing/apply_patches.sh && \
    python3 -m pip install -r turing/requirements.txt --break-system-packages

RUN cat <<EOF >> /root/turing/Turing/settings.ini
[settings]
SECRET_KEY=ab&v1v}7G+$*m$pg:zkUNHUhhYA&yKuWPETi!r{b?T{UXKuj=t
DEBUG=True
DEV_MODE=False
ALLOWED_HOSTS=*
INTERNAL_IPS=127.0.0.1
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
REGISTRATION_OPEN=
EOF

RUN ln -s /mnt/database/db.sqlite3 turing/

# Part 2: test dependencies
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt update -y -q && \
    apt install -y -qq google-chrome-stable

RUN apt install -y -qq unzip && \
    LATEST_STABLE_RELEASE=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    CHROME_BASE_URL=https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$LATEST_STABLE_RELEASE && \
    wget -O /tmp/chromedriver.zip $CHROME_BASE_URL/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    rm -rf /tmp/chrome*

RUN python3 -m pip install -r turing/requirements-dev.txt --break-system-packages

# The end: run server on docker container start
CMD cd turing && python3 manage.py runserver 0.0.0.0:8080
