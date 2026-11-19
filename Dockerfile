FROM python:3.11-slim

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install FFmpeg with libass support, NodeJS (for yt-dlp JS challenge deciphering), and font/OpenCV dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    fontconfig \
    fonts-freefont-ttf \
    fonts-liberation \
    fonts-dejavu \
    libgl1 \
    libglib2.0-0 \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft Core Fonts (includes Impact, Arial) & refresh font cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    cabextract \
    xfonts-utils \
    && wget https://www.freedesktop.org/software/fontconfig/webfonts/webfonts.tar.gz -O /tmp/webfonts.tar.gz || true \
    && rm -rf /var/lib/apt/lists/* || true \
    && fc-cache -f -v

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY scripts/ ./scripts/
COPY app.py .

# Create persistent/runtime directories
RUN mkdir -p /app/temp_work /app/final_clips

# Default port for Render
ENV PORT=8000
EXPOSE 8000

# Start FastAPI server
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
