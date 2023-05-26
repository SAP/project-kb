FROM python:3.10-slim

RUN pip install --upgrade pip
RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev python3-dev libpq-dev git curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
RUN apt autoremove -y gcc g++ libffi-dev python3-dev && apt clean && rm -rf /var/lib/apt/lists/*
