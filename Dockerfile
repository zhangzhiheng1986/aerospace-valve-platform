FROM python:3.11-slim

# Install system deps for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies first (layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy application code
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

WORKDIR /app/backend

# Create data directory for SQLite & user data
RUN mkdir -p /app/backend/data && \
    chmod 777 /app/backend/data

EXPOSE 5000

# Use gunicorn in production (wsgi.py is the v2 Blueprint-compatible entry point)
ENV PORT=5000
CMD gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120 wsgi:app