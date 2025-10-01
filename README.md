# gen5-retro-tracker

A Gen 5 Retro Tracker project with Jarvis prototype API for voice command processing and AI integration.

## Features

- 🤖 **Jarvis Prototype API**: Minimal API for command processing
- 🔒 **Bearer Token Authentication**: Secure API endpoints
- 🐳 **Docker Support**: Easy deployment with docker-compose
- 📝 **Health Monitoring**: Built-in health check endpoints
- 🚀 **Fast Setup**: Quick start with helper scripts

## Prerequisites

- Docker and Docker Compose
- Git
- (Optional) curl for testing API endpoints

## Quick Start

### 1. Setup Environment

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

Edit `.env` and configure:
- `BEARER_TOKEN`: Set a secure token for API authentication
- `API_SECRET_KEY`: Set a secret key for the API
- Other variables as needed

### 2. Build and Start Services

Using docker-compose directly:

```bash
docker compose up --build -d
```

Or using the start script:

```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

The start script supports several options:
```bash
./scripts/start.sh --help        # Show all available options
./scripts/start.sh --follow      # Start and follow logs
./scripts/start.sh --sudo        # Use sudo for docker commands
```

### 3. Verify Services

Check that services are running:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f jarvis
```

## Calling the API

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "jarvis-prototype",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Send a Command

Replace `YOUR_BEARER_TOKEN` with the token from your `.env` file:

```bash
curl -X POST http://localhost:8000/api/v1/command \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "hello", "parameters": {}}'
```

Expected response:
```json
{
  "success": true,
  "message": "Command executed successfully",
  "result": {
    "response": "Hello from Jarvis!"
  },
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

### Available Commands

- `hello`: Get a greeting from Jarvis
- `status`: Check system status

Example status command:

```bash
curl -X POST http://localhost:8000/api/v1/command \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "status"}'
```

## API Documentation

Once the service is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Development

### Project Structure

```
gen5-retro-tracker/
├── jarvis/                 # Jarvis API source code
│   ├── main.py            # Main API application
│   └── requirements.txt   # Python dependencies
├── scripts/               # Helper scripts
│   └── start.sh          # Startup script
├── docker-compose.yml    # Docker compose configuration
├── Dockerfile            # Docker image definition
├── .env.example          # Environment template
└── README.md             # This file
```

### Making Changes

1. Edit files in the `jarvis/` directory
2. Rebuild the container:
   ```bash
   docker compose up --build -d
   ```

### Stopping Services

```bash
docker compose down
```

To remove volumes as well:

```bash
docker compose down -v
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, change `API_PORT` in your `.env` file:

```bash
API_PORT=8001
```

### Permission Denied

If you get permission errors with Docker, try using the `--sudo` flag:

```bash
./scripts/start.sh --sudo
```

### Container Won't Start

Check logs for errors:

```bash
docker compose logs jarvis
```

## Contributing

This is part of the Gen 5 project ecosystem. See related repositories:
- bhujang
- doos

## License

See repository license file for details.