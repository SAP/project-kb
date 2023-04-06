FROM python:3.10-slim

WORKDIR /app
COPY . .
COPY docker/service/start.sh /app/start.sh
COPY ./config-sample.yaml /app/config.yaml
RUN chmod +x /app/start.sh
COPY ./service/ /app
RUN pip install --upgrade pip
RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev python3-dev libpq-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
RUN apt autoremove -y gcc g++ libffi-dev python3-dev && apt clean && rm -rf /var/lib/apt/lists/*
ENV PYTHONPATH .
#RUN rm -rf /app/rules
RUN mkdir /app/cve_data

#CMD tail -f /dev/null
CMD ["python","./main.py"]
