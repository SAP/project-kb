FROM python:3.10-slim

RUN mkdir -p /app
COPY ./requirements.txt /app/
WORKDIR /app
# Create log files with permissions for host user
RUN touch evaluation.log
RUN touch prospector.log
RUN chown ${UID}:${GID} evaluation.log
RUN chown ${UID}:${GID} prospector.log

# Install dependencies with pip
RUN pip install --upgrade pip
RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev python3-dev libpq-dev git curl
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
RUN apt autoremove -y gcc g++ libffi-dev python3-dev && apt clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH "${PYTHONPATH}:/app"
