FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    gcc \
    git \
    tree \
    libpq-dev \
    gdal-bin libgdal-dev \
    libproj-dev libgeos-dev binutils \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip 

COPY requirements.txt .

RUN  pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
