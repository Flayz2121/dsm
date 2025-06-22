FROM python:3.9-slim
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip setuptools
COPY requirements.txt ./
RUN pip install -r requirements.txt -v
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
