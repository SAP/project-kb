FROM python:3.8.13-slim


ADD . .
COPY docker/api/update-feeds.sh /app/update-feeds.sh
RUN chmod +x /app/update-feeds.sh
COPY ./api /app
RUN pip install --upgrade pip
RUN pip install pipenv
RUN apt update && apt install -y --no-install-recommends gcc g++ libffi-dev
RUN pipenv install --system --deploy --ignore-pipfile
RUN apt autoremove -y gcc g++ libffi-dev && apt clean && rm -rf /var/lib/apt/lists/*
ENV GIT_CACHE /tmp
ENV CVE_DATA_PATH /cve_data
ENV REDIS_URL redis://redis:6379/0
ENV POSTGRES_HOST db
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER postgres
ENV POSTGRES_DBNAME postgres
ENV PYTHONPATH .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]