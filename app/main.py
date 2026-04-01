"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes_events import router as events_router
from app.api.routes_ops import router as ops_router
from app.database import Base, engine
from app.seed_data import ensure_runbooks_exist
from app.services.metrics_service import metrics_store

Base.metadata.create_all(bind=engine)
ensure_runbooks_exist()

app = FastAPI(
    title="Remote Operations Assistant",
    description="Starter project for multi-site industrial monitoring and guided response.",
    version="1.0.0",
)

app.include_router(events_router)
app.include_router(ops_router)


@app.get("/")
def read_root():
    return {
        "message": "Remote Operations Assistant is running.",
        "main_input": "Operational events through REST API",
        "operator_output": [
            "/ops/incidents",
            "/ops/ranked-actions",
            "/ops/shift-summary",
            "/ops/metrics",
        ],
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    metrics_store.record_total()
    metrics_store.record_validation_rejected()
    return JSONResponse(
        status_code=422,
        content={
            "accepted": False,
            "reason": "validation_error",
            "details": exc.errors(),
        },
    )