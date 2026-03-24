"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes_events import router as events_router
from app.api.routes_ops import router as ops_router
from app.database import Base, engine
from app.seed_data import ensure_runbooks_exist

# Ensure local tables exist when the application starts.
Base.metadata.create_all(bind=engine)

# Ensure the sample local knowledge base exists.
ensure_runbooks_exist()

app = FastAPI(
    title="Remote Operations Assistant",
    description="Starter project for multi-site industrial monitoring and guided response.",
    version="1.0.0",
)

# Register API route groups.
app.include_router(events_router)
app.include_router(ops_router)


@app.get("/")
def read_root():
    """Basic health endpoint."""
    return {
        "message": "Remote Operations Assistant is running.",
        "main_input": "Operational events through REST API",
        "operator_output": [
            "/ops/incidents",
            "/ops/ranked-actions",
            "/ops/shift-summary",
        ],
    }
