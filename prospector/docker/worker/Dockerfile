#FROM python:3.10-slim
#
#LABEL Author="Antonino Sabetta <antonino.sabetta@sap.com>"
#
## NOTICE
##
## This dockerfile is based on https://github.com/geekinutah/docker-python-rq-worker
## by Mike Wilson <geekinutah@gmail.com>
##
## It was modified to work with alpine instead of ubuntu; a few of the
## original dependencies were dropped too to make the image even slimmer
#
#ENV TERM=xterm-256color
#ENV REDIS_HOST=redis
#ENV REDIS_PORT=6379
#ENV REDIS_DB=0
#ENV RQ_QUEUE=default
#ENV LOG_LEVEL=DEBUG
#ENV PIP_PACKAGES=none
#ENV PIP_REQUIREMENTS=none
#ENV LC_ALL=C.UTF-8
#ENV LANG=C.UTF-8
#
#RUN pip install --upgrade pip
#RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev python3-dev libpq-dev git supervisor curl
#
#COPY requirements.txt /requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#RUN python -m spacy download en_core_web_sm
#COPY docker/worker/start_rq_worker.sh /usr/local/bin/start_rq_worker.sh
## COPY etc_supervisor_confd_rqworker.conf.j2 /etc/supervisor/conf.d/rqworker.conf.j2
#COPY docker/worker/etc_supervisor_confd_rqworker.conf.j2 /etc/supervisor.d/rqworker.ini.j2
#VOLUME ["/pythonimports"]
#ENV PYTHONPATH "${PYTHONPATH}:/pythonimports"
#
##CMD tail -f /dev/null
#RUN chmod +x /usr/local/bin/start_rq_worker.sh
#ENTRYPOINT ["/usr/local/bin/start_rq_worker.sh"]
#

FROM prospector-base:1.0

#LABEL Author="Antonino Sabetta <antonino.sabetta@sap.com>"
#
## NOTICE
##
## This dockerfile is based on https://github.com/geekinutah/docker-python-rq-worker
## by Mike Wilson <geekinutah@gmail.com>
##
## It was modified to work with alpine instead of ubuntu; a few of the
## original dependencies were dropped too to make the image even slimmer

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

RUN apt update && apt install -y --no-install-recommends supervisor

COPY docker/worker/start_rq_worker.sh /usr/local/bin/start_rq_worker.sh
COPY docker/worker/etc_supervisor_confd_rqworker.conf.j2 /etc/supervisor.d/rqworker.ini.j2

#VOLUME ["/pythonimports"]
#ENV PYTHONPATH "${PYTHONPATH}:/pythonimports"

VOLUME [ "/data_sources/reports" ]

RUN chmod +x /usr/local/bin/start_rq_worker.sh
#CMD tail -f /dev/null

# Create directory for gitcache and run git config command to avoid 'dubious ownership' error
RUN mkdir -p /tmp/gitcache && \
    cd /tmp/gitcache && \
    git config --global --add safe.directory '*'


ENTRYPOINT ["/usr/local/bin/start_rq_worker.sh"]
