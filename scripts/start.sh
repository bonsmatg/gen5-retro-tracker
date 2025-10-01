#!/usr/bin/env bash
set -euo pipefail

# Defaults (override with flags)
USE_SUDO=false
IPFS_PROFILE=false
FOLLOW_LOGS=false
COMPOSE_FILE=""
PROJECT_DIR="$(pwd)"

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

A defensive startup script for the Gen5 Retro Tracker development environment.

OPTIONS:
  -s, --sudo              Use sudo for docker commands
  -i, --ipfs              Enable IPFS profile
  -f, --follow            Follow logs after startup
  -c, --compose FILE      Specify custom docker-compose file
  -d, --dir DIRECTORY     Set project directory (default: current directory)
  -h, --help              Show this help message

EXAMPLES:
  $0                      # Start with defaults
  $0 --follow             # Start and follow logs
  $0 --sudo --follow      # Start with sudo and follow logs
  $0 -c custom.yml        # Start with custom compose file

EOF
  exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -s|--sudo)
      USE_SUDO=true
      shift
      ;;
    -i|--ipfs)
      IPFS_PROFILE=true
      shift
      ;;
    -f|--follow)
      FOLLOW_LOGS=true
      shift
      ;;
    -c|--compose)
      COMPOSE_FILE="$2"
      shift 2
      ;;
    -d|--dir)
      PROJECT_DIR="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Change to project directory
cd "$PROJECT_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
  echo "WARNING: .env file not found!"
  if [ -f .env.example ]; then
    echo "Please copy .env.example to .env and fill in the values:"
    echo "  cp .env.example .env"
    exit 1
  else
    echo "Please create a .env file with required environment variables."
    exit 1
  fi
fi

# Build docker command
DOCKER_CMD="docker"
if [ "$USE_SUDO" = true ]; then
  DOCKER_CMD="sudo docker"
fi

# Determine compose file
COMPOSE_ARGS=""
if [ -n "$COMPOSE_FILE" ]; then
  if [ ! -f "$COMPOSE_FILE" ]; then
    echo "ERROR: Compose file not found: $COMPOSE_FILE"
    exit 1
  fi
  COMPOSE_ARGS="-f $COMPOSE_FILE"
else
  if [ ! -f docker-compose.yml ]; then
    echo "ERROR: docker-compose.yml not found in $PROJECT_DIR"
    exit 1
  fi
fi

# Set IPFS profile if requested
if [ "$IPFS_PROFILE" = true ]; then
  export IPFS_PROFILE=server
  echo "Using IPFS profile: server"
fi

# Stop any running containers
echo "Stopping any running containers..."
$DOCKER_CMD compose $COMPOSE_ARGS down || true

# Build and start services
echo "Building and starting services..."
$DOCKER_CMD compose $COMPOSE_ARGS up --build -d

# Check if services started successfully
if [ $? -eq 0 ]; then
  echo "✓ Services started successfully!"
  echo ""
  echo "Running services:"
  $DOCKER_CMD compose $COMPOSE_ARGS ps
  echo ""
  echo "API endpoints:"
  echo "  Health check: http://localhost:8000/health"
  echo "  Command API:  http://localhost:8000/api/v1/command"
  echo ""
  
  # Follow logs if requested
  if [ "$FOLLOW_LOGS" = true ]; then
    echo "Following logs (press Ctrl+C to exit)..."
    $DOCKER_CMD compose $COMPOSE_ARGS logs -f
  else
    echo "To view logs, run:"
    echo "  $DOCKER_CMD compose $COMPOSE_ARGS logs -f"
  fi
else
  echo "✗ Failed to start services"
  exit 1
fi
