import logging
from fastapi import FastAPI, HTTPException, status
import redis
import psycopg2

from src.config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("agent-manager")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise Infrastructure Agent Manager Microservice"
)

def check_redis() -> bool:
    try:
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, socket_timeout=2)
        return bool(r.ping())
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False

def check_postgres() -> bool:
    try:
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            connect_timeout=3
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return False

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "environment": settings.ENV
    }

@app.get("/health", status_code=status.HTTP_200_OK)
def liveness():
    """Liveness probe endpoint for container orchestrators (Kubernetes / Docker)."""
    return {"status": "alive"}

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness():
    """Readiness probe endpoint: verifies active connection pool to DB and Redis broker."""
    redis_ok = check_redis()
    db_ok = check_postgres()

    if redis_ok and db_ok:
        return {
            "status": "ready",
            "dependencies": {
                "postgres": "connected",
                "redis": "connected"
            }
        }
    
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "status": "unhealthy",
            "dependencies": {
                "postgres": "connected" if db_ok else "disconnected",
                "redis": "connected" if redis_ok else "disconnected"
            }
        }
    )

@app.get("/api/v1/agents", status_code=status.HTTP_200_OK)
def list_agents():
    """Retrieves current infrastructure monitoring and execution agents."""
    return {
        "total_agents": 3,
        "agents": [
            {"id": "agent-01", "type": "monitoring", "status": "active", "node": "k8s-node-01"},
            {"id": "agent-02", "type": "task-runner", "status": "active", "node": "k8s-node-02"},
            {"id": "agent-03", "type": "log-aggregator", "status": "active", "node": "k8s-node-03"}
        ]
    }
