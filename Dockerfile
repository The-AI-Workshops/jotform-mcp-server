# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for certain Python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir --upgrade pip uv

# Copy project definition and lock file
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
# This leverages the lock file for reproducible installs
# It creates a virtual environment within the image for isolation
RUN uv venv /opt/venv && \
    uv pip sync --python /opt/venv/bin/python uv.lock

# Activate the virtual environment for subsequent commands
ENV PATH="/opt/venv/bin:$PATH"

# Copy the rest of the application code into the container
# Copy application code after installing dependencies to leverage Docker cache
COPY . .

# Make port 8067 available to the world outside this container
# This is the port the MCP server listens on, defined in .env and jotform_mcp_server.py
EXPOSE 8067

# Define environment variables needed by the application
# The API key should be passed at runtime for security, not baked into the image.
# Set defaults for others if not provided at runtime.
ENV MCP_HOST="0.0.0.0"
ENV MCP_PORT="8067"
ENV MCP_TRANSPORT="sse"
ENV JOTFORM_BASE_URL="https://api.jotform.com/"
ENV JOTFORM_OUTPUT_TYPE="json"
ENV JOTFORM_DEBUG_MODE="False"
# JOTFORM_API_KEY must be provided at runtime, e.g., docker run -e JOTFORM_API_KEY=...

# Run jotform_mcp_server.py when the container launches
# Use CMD to allow overriding the command easily
CMD ["python", "jotform_mcp_server.py"]
