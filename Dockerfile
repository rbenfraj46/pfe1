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
    libproj-dev \
    gettext \
    netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=carrent.settings_dev

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
