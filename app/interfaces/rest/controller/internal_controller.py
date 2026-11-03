from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.query_service.default_job_search_query_service import DefaultJobSearchQueryService
from app.dependencies import get_current_user_id, get_db_session, get_job_search_query_service
from app.interfaces.rest.resources.job_resource import JobResource
from app.interfaces.rest.transform.job_resource_from_entity_assembler import JobResourceFromEntityAssembler


router = APIRouter(prefix="/api/v1/internal", tags=["Internal"])


@router.get("/favorites/{job_id}", response_model=JobResource)
async def get_favorite_job(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> JobResource:
    service: DefaultJobSearchQueryService = get_job_search_query_service(session)
    job = await service.handle_get_favorite_by_job_id(user_id, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite job not found.")
    return JobResourceFromEntityAssembler.to_resource(job)
