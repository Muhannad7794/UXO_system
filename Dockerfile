# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /UXO_system_dockerized

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev libjpeg-dev zlib1g-dev pkg-config \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /UXO_system_dockerized/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy code
COPY . /UXO_system_dockerized/

# Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
