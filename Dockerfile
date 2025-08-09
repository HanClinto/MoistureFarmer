# Use a slim Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies (if any needed later, add here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies first for better layer caching
COPY code/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the application code
COPY code/ /app/

# Expose the port uvicorn will listen on
EXPOSE 8000

# Default command to run the FastAPI app
# Bind to 0.0.0.0 so it's accessible outside the container
CMD ["uvicorn", "webgui.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
