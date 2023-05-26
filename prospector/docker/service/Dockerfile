#FROM python:3.10-slim
#VOLUME ["/app"]
##COPY docker/service/start.sh /app/start.sh
##COPY ./config-sample.yaml /app/config.yaml
##RUN chmod +x /app/start.sh
##COPY ./service/ /app
#RUN pip install --upgrade pip
#RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev python3-dev libpq-dev
#COPY requirements.txt /requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#RUN python -m spacy download en_core_web_sm
#RUN apt autoremove -y gcc g++ libffi-dev python3-dev && apt clean && rm -rf /var/lib/apt/lists/*
#ENV PYTHONPATH "${PYTHONPATH}:/app"
##RUN rm -rf /app/rules
##RUN mkdir /app/cve_data
#WORKDIR /app
##CMD tail -f /dev/null
#CMD ["python","./service/main.py"]

FROM prospector-base:1.0

VOLUME ["/app"]
ENV PYTHONPATH "${PYTHONPATH}:/app"
WORKDIR /app

CMD ["python","./service/main.py"]
