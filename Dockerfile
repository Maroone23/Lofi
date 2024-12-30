FROM python:3.9-slim

# Install system dependencies including FFmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    rubberband-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set system limits for file size
RUN echo "* soft nofile 65535" >> /etc/security/limits.conf && \
    echo "* hard nofile 65535" >> /etc/security/limits.conf

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Verify FFmpeg installation
RUN ffmpeg -version

# Set environment variables for larger file handling
ENV GUNICORN_TIMEOUT=600
ENV GUNICORN_WORKERS=2
ENV GUNICORN_THREADS=4

# Command to run the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--timeout", "600", "--workers", "2", "--threads", "4"]
