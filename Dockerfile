# Dockerfile.gis - For the add_GIS branch (connecting to Azure DB)

# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /UXO_system_dockerized_gis

# First, copy only the requirements file to leverage Docker's layer caching.
# Assumes requirements.txt is in the same directory as this Dockerfile.gis
COPY ./requirements.txt .

# Install system dependencies needed for GeoDjango (GDAL, GEOS, PROJ) and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    postgresql-client \
    libgdal-dev \
    build-essential && \
    # Now, install Python packages
    pip install --no-cache-dir -r requirements.txt && \
    # Clean up apt cache to keep the image slim
    apt-get purge -y --auto-remove build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Now copy the rest of the application code into the container
COPY . .

# CMD is managed by docker-compose.gis.yml