"""
FastAPI backend application for Neo4j EDGAR Graph Visualization UI.
"""

import os
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Setup logging
from utils.logger_config import setup_logger, get_logger
setup_logger(app_name="ui_backend")
logger = get_logger(__name__)

from api import graph, ticker

app = FastAPI(
    title="Neo4j EDGAR Graph API",
    description="REST API for querying Neo4j EDGAR graph database",
    version="1.0.0"
)

# Request logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.bind(access=True).info(
            f"Request: {request.method} {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'} | "
            f"Query params: {dict(request.query_params)}"
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.bind(access=True).info(
                f"Response: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Time: {process_time:.3f}s"
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} | "
                f"Exception: {str(e)} | "
                f"Time: {process_time:.3f}s",
                exc_info=True
            )
            raise

# Add middleware (order matters - logging first, then CORS)
app.add_middleware(LoggingMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(graph.router, prefix="/api", tags=["graph"])
app.include_router(ticker.router, prefix="/api", tags=["ticker"])


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("=" * 60)
    logger.info("Neo4j EDGAR Graph API - Starting")
    logger.info("=" * 60)
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Neo4j URI: {os.getenv('NEO4J_URI', 'bolt://localhost:7687')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("=" * 60)
    logger.info("Neo4j EDGAR Graph API - Shutting down")
    logger.info("=" * 60)


@app.get("/")
async def root():
    """Root endpoint"""
    logger.debug("Root endpoint accessed")
    return {
        "message": "Neo4j EDGAR Graph API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}

