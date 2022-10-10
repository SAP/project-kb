#!/bin/sh

# COPYRIGHT NOTICE
#
# This code comes from https://github.com/geekinutah/docker-python-rq-worker
# (with minor modifications to make it work with alpine instead of ubuntu)

if [ "${PIP_PACKAGES}" != 'none' ]; then
    for i in $(echo "${PIP_PACKAGES}" | sed 's/,/ /g'); do
        pip3 install $i
    done
fi

# If there is a requirements file, install that

if [ "${PIP_REQUIREMENTS}" != 'none' ]; then
    pip3 install -r "${PIP_REQUIREMENTS}"
fi

cat /etc/supervisor.d/rqworker.ini.j2 | python3 -c 'import os;import sys; import jinja2; sys.stdout.write(jinja2.Template(sys.stdin.read()).render(env=os.environ))' > /etc/supervisor.d/rqworker.ini

supervisord -n
