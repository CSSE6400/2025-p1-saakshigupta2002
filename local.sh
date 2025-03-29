#!/bin/bash

# Stop and remove any existing container
docker stop coughoverflow-pas >/dev/null 2>&1 || true
docker rm coughoverflow-pas >/dev/null 2>&1 || true

# Build the Docker image
docker build -t coughoverflow-pas .

# Run the container in detached mode
docker run -d -p 8080:8080 --name coughoverflow-pas coughoverflow-pas

# Wait for the server to be ready
echo "Waiting for server to start..."
for i in {1..20}; do
  if curl -s http://localhost:8080/api/v1/health > /dev/null; then
    echo "Server is up and running!"
    break
  fi
  echo "Attempt $i/20: Server not ready yet, waiting 3 seconds..."
  sleep 3
  if [ $i -eq 20 ]; then
    echo "Server might not be fully started yet, but continuing anyway."
  fi
done

# If running in GitHub Actions, don't keep the script running
if [ -n "$GITHUB_ACTIONS" ]; then
  echo "Running in GitHub Actions - exiting script to allow workflow to continue"
  exit 0
fi

# For local development, show logs
docker logs -f coughoverflow-pas