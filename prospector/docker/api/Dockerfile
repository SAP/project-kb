FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8


ADD . .
COPY ./api /app
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile
ENV GIT_CACHE /tmp
ENV CVE_DATA_PATH /cve_data
ENV REDIS_URL redis://redis:6379/0
ENV POSTGRES_HOST db
ENV POSTGRES_PORT 5432
ENV POSTGRES_USER postgres
ENV POSTGRES_DBNAME postgres
ENV PYTHONPATH .
RUN python api/routers/nvd_feed_update.py
