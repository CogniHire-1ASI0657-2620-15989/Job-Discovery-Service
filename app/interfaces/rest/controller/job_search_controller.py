from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_job_search_command_service import DefaultJobSearchCommandService
from app.application.internal.query_service.default_job_search_query_service import DefaultJobSearchQueryService
from app.dependencies import get_current_user_id, get_db_session, get_job_search_command_service, get_job_search_query_service
from app.domain.model.queries.get_favorite_jobs_query import GetFavoriteJobsQuery
from app.domain.model.queries.get_job_by_id_query import GetJobByIdQuery
from app.interfaces.rest.resources.favorite_job_resources import FavoriteListResource, FavoriteMutationResource
from app.interfaces.rest.resources.job_resource import JobResource
from app.interfaces.rest.resources.job_search_response_resource import JobSearchResponseResource
from app.interfaces.rest.resources.search_jobs_resource import SearchJobsResource
from app.interfaces.rest.transform.favorite_job_command_from_resource_assembler import FavoriteJobCommandFromResourceAssembler
from app.interfaces.rest.transform.job_resource_from_entity_assembler import JobResourceFromEntityAssembler
from app.interfaces.rest.transform.search_jobs_command_from_resource_assembler import SearchJobsCommandFromResourceAssembler


router = APIRouter(prefix="/api/v1", tags=["Job Search"])


@router.get("/jobs", response_model=JobSearchResponseResource)
async def search_jobs(
    resource: SearchJobsResource = Depends(),
    _: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> JobSearchResponseResource:
    command = SearchJobsCommandFromResourceAssembler.to_command(resource)
    service: DefaultJobSearchCommandService = get_job_search_command_service(session)
    offers, total, provider_status = await service.handle_search(command)
    return JobSearchResponseResource(
        items=[JobResourceFromEntityAssembler.to_resource(offer) for offer in offers],
        total=total,
        page=resource.page,
        page_size=resource.page_size,
        provider_status=provider_status,
    )


@router.get("/jobs/{job_id}", response_model=JobResource)
async def get_job(job_id: int, _: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> JobResource:
    service: DefaultJobSearchQueryService = get_job_search_query_service(session)
    offer = await service.handle_get_job_by_id(GetJobByIdQuery(job_offer_id=job_id))
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job offer not found.")
    return JobResourceFromEntityAssembler.to_resource(offer)


@router.post("/jobs/{job_id}/favorite", response_model=FavoriteMutationResource)
async def add_favorite(job_id: int, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> FavoriteMutationResource:
    command = FavoriteJobCommandFromResourceAssembler.to_add_command(user_id, job_id)
    service: DefaultJobSearchCommandService = get_job_search_command_service(session)
    offer, created = await service.handle_add_favorite(command)
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job offer not found.")
    return FavoriteMutationResource(job=JobResourceFromEntityAssembler.to_resource(offer), created=created)


@router.delete("/jobs/{job_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(job_id: int, user_id: int = Depends(get_current_user_id), session: AsyncSession = Depends(get_db_session)) -> None:
    command = FavoriteJobCommandFromResourceAssembler.to_remove_command(user_id, job_id)
    service: DefaultJobSearchCommandService = get_job_search_command_service(session)
    await service.handle_remove_favorite(command)


@router.get("/favorites", response_model=FavoriteListResource)
async def list_favorites(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> FavoriteListResource:
    query = GetFavoriteJobsQuery(user_id=user_id, page=page, page_size=page_size)
    service: DefaultJobSearchQueryService = get_job_search_query_service(session)
    offers, total = await service.handle_get_favorites(query)
    return FavoriteListResource(
        items=[JobResourceFromEntityAssembler.to_resource(offer) for offer in offers],
        total=total,
        page=page,
        page_size=page_size,
    )
