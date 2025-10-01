"""
Jarvis Prototype API for Gen5 Retro Tracker
A minimal API server for command processing and health checks
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="Jarvis Prototype API",
    description="Gen5 Retro Tracker - Minimal Jarvis API",
    version="0.1.0"
)

# Load configuration from environment
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class CommandRequest(BaseModel):
    """Command request model"""
    command: str
    parameters: Optional[Dict[str, Any]] = None


class CommandResponse(BaseModel):
    """Command response model"""
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    timestamp: str


def verify_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verify bearer token authentication"""
    if not BEARER_TOKEN:
        # If no token is configured, allow access (development mode)
        return True
    
    if not authorization:
        return False
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    
    return parts[1] == BEARER_TOKEN


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    Returns the API status and basic information
    """
    return {
        "status": "healthy",
        "service": "jarvis-prototype",
        "version": "0.1.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/command", response_model=CommandResponse)
async def process_command(
    request: CommandRequest,
    authorization: Optional[str] = Header(None)
) -> CommandResponse:
    """
    Process a command request
    Requires bearer token authentication
    """
    # Verify authentication
    if not verify_token(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Process the command (placeholder implementation)
    command = request.command.lower().strip()
    
    # Basic command processing
    if command == "hello":
        return CommandResponse(
            success=True,
            message="Command executed successfully",
            result={"response": "Hello from Jarvis!"},
            timestamp=datetime.utcnow().isoformat()
        )
    elif command == "status":
        return CommandResponse(
            success=True,
            message="Command executed successfully",
            result={
                "system_status": "operational",
                "active_tasks": 0,
                "uptime": "running"
            },
            timestamp=datetime.utcnow().isoformat()
        )
    else:
        return CommandResponse(
            success=False,
            message=f"Unknown command: {request.command}",
            result=None,
            timestamp=datetime.utcnow().isoformat()
        )


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "message": "Jarvis Prototype API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if ENVIRONMENT == "development" else False
    )
