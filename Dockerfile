FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

EXPOSE 80

CMD exec gunicorn app.main:app -b 0.0.0.0:${PORT} --timeout 120
