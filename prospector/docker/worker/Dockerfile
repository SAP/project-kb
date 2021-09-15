FROM alpine:3.13.4

LABEL Author="Antonino Sabetta <antonino.sabetta@sap.com>"

# NOTICE
#
# This dockerfile is based on https://github.com/geekinutah/docker-python-rq-worker
# by Mike Wilson <geekinutah@gmail.com>
#
# It was modified to work with alpine instead of ubuntu; a few of the
# original dependencies were dropped too to make the image even slimmer

ENV TERM=xterm-256color
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_DB=0
ENV RQ_QUEUE=default
ENV LOG_LEVEL=DEBUG
ENV PIP_PACKAGES=none
ENV PIP_REQUIREMENTS=none
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apk add python3 py3-pip git supervisor curl \
    && pip3 install rq \
    && pip3 install Jinja2 \
    && rm  -rf /tmp/* /var/cache/apk/*

COPY requirements.txt /requirements.txt
COPY start_rq_worker.sh /usr/bin/start_rq_worker.sh
# COPY etc_supervisor_confd_rqworker.conf.j2 /etc/supervisor/conf.d/rqworker.conf.j2
COPY etc_supervisor_confd_rqworker.conf.j2 /etc/supervisor.d/rqworker.ini.j2
VOLUME ["/pythonimports"]

RUN chmod +x /usr/bin/start_rq_worker.sh
ENTRYPOINT ["/usr/bin/start_rq_worker.sh"]
