# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency files to working directory
COPY requirements.txt requirements.txt

# Complete installation and execution in a single RUN command
# 1. Update package list and install curl
# 2. Download and execute uv installation script
# 3. Use uv's correct absolute path with --system parameter to install Python dependencies
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --no-cache --system -r requirements.txt

# Copy your application code to working directory
COPY openwrt.py .

# Expose the port your application runs on
EXPOSE 8444

# Set the command to run when container starts
CMD ["python", "./openwrt.py"]