# Stage 1: Build environment
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libx11-dev \
    libgtk-3-dev \
    libboost-dev \
    libboost-python-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libgtk-3-0 \
    libboost-python-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from the builder stage
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app /app

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]