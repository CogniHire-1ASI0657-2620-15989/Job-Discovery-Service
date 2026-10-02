from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.configuration.settings import get_settings
from app.interfaces.rest.controller.job_search_controller import router as jobs_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Validate settings early. Schema changes are intentionally handled by Alembic.
    get_settings()
    yield


app = FastAPI(
    title="Job-Search Service",
    description="Job search and favorites service backed by Jooble Peru.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(jobs_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"service": "job-search", "status": "healthy"}
