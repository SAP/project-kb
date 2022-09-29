<<<<<<< HEAD
=======
#FROM flyingjoe/uvicorn-gunicorn-fastapi:python3.8-slim
#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
>>>>>>> origin/prospector-assuremoss
FROM python:3.8-slim

WORKDIR /app
ADD . .
COPY docker/api/start.sh /app/start.sh
RUN chmod +x /app/start.sh
COPY ./api /app
RUN pip install --upgrade pip
RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev python3-dev libpq-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN apt autoremove -y gcc g++ libffi-dev python3-dev && apt clean && rm -rf /var/lib/apt/lists/*
<<<<<<< HEAD
=======
ENV GIT_CACHE /tmp
ENV CVE_DATA_PATH /cve_data
ENV REDIS_URL redis://redis:6379/0
ENV POSTGRES_HOST db
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER postgres
ENV POSTGRES_DBNAME postgres
>>>>>>> origin/prospector-assuremoss
ENV PYTHONPATH .

CMD ["./start.sh"]