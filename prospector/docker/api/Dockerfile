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
ENV PYTHONPATH .

CMD ["./start.sh"]
