FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    libjpeg-dev \
    libfreetype6-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    binutils \
    libproj-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip && \
    pip install -e .

EXPOSE 8000


ENV DJANGO_SETTINGS_MODULE=carrent.settings_dev

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
