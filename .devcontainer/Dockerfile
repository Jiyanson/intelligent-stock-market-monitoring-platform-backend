# Start from same base as production Dockerfile
FROM python:3.10-slim

# System dependencies for dev
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    git \
    vim \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Create work dir
WORKDIR /code

# Copy and install requirements
COPY ../requirements.txt ../dev-requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt -r dev-requirements.txt

# Default shell setup
CMD ["bash"]
