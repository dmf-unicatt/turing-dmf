# Copyright (C) 2024 by the Turing @ DMF authors
#
# This file is part of Turing @ DMF.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM debian:12
MAINTAINER Francesco Ballarin <francesco.ballarin@unicatt.it>

WORKDIR /root

COPY turing turing

RUN apt update -y -q && \
    apt install -y -qq net-tools python3-pip vim

RUN python3 -m pip install -r turing/requirements.txt --break-system-packages

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

RUN cd turing && \
    python3 manage.py makemigrations && \
    python3 manage.py makemigrations engine && \
    python3 manage.py migrate && \
    DJANGO_SUPERUSER_EMAIL=admin@admin.it DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=admin python3 manage.py createsuperuser --no-input

CMD cd turing && python3 manage.py runserver 0.0.0.0:8080
