FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN dpkg --print-architecture | grep -q "amd64" && export ARCH="amd64" || export ARCH="arm64" && \
    wget https://github.com/CSSE6400/CoughOverflow-Engine/releases/download/v1.0/overflowengine-${ARCH} -O /usr/local/bin/overflowengine && \
    chmod +x /usr/local/bin/overflowengine

# After downloading overflowengine
RUN /usr/local/bin/overflowengine --help || echo "Overflowengine installation failed!"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/uploads
RUN mkdir -p /app/results

# Copy labs.csv file
COPY labs.csv /app/labs.csv

# Copy the application code
COPY . /app/

# Expose the port
EXPOSE 8080

# Command to run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]