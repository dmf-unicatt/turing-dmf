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
    apt install -y -qq curl git net-tools python3-pip sudo unzip vim wget

# Part 1: turing
COPY patches patches
COPY turing turing
COPY .git/modules/turing turing/.git

RUN sed -i "/worktree =/d" turing/.git/config && patches/turing/apply_patches.sh

RUN apt install -y -qq libpq-dev postgresql postgresql-client postgresql-contrib python3-psycopg2 python3-selenium && \
    echo "$POSTGRES_PASSWORD\n$POSTGRES_PASSWORD" | passwd postgres

# postgres has created a new user, which should be allow read-only access to /root
RUN chmod go+rx /root

RUN python3 -m pip install --break-system-packages -r turing/requirements.txt && \
    python3 -m pip install --break-system-packages -r turing/requirements-dev.txt

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

RUN cd /root/turing && \
    python3 manage.py collectstatic

# Part 2: mathrace-interaction
COPY mathrace_interaction mathrace_interaction

RUN cd /root/mathrace_interaction && \
    python3 -m pip install --break-system-packages .[tests]

# Part 3: set up entrypoint that:
# * creates and initialize databases on first run,
# * starts the server
COPY docker/entrypoint.sh /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]
