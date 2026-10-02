from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.internal.command_services.default_job_search_command_service import DefaultJobSearchCommandService
from app.application.internal.query_service.default_job_search_query_service import DefaultJobSearchQueryService
from app.infrastructure.configuration.settings import get_settings
from app.infrastructure.persistence.sqlalchemy.database import get_session
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_favorite_job_repository import SQLAlchemyFavoriteJobRepository
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_job_offer_repository import SQLAlchemyJobOfferRepository
from app.infrastructure.providers.jooble_peru_provider import JooblePeruProvider


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


def get_current_user_id(request: Request) -> int:
    header = get_settings().gateway_user_id_header
    raw_user_id = request.headers.get(header)
    if raw_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Missing gateway identity header: {header}")
    try:
        user_id = int(raw_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.") from exc
    if user_id <= 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid gateway user identifier.")
    return user_id


def get_job_provider() -> JooblePeruProvider:
    settings = get_settings()
    return JooblePeruProvider(settings.jooble_api_key, settings.jooble_base_url)


def get_job_search_command_service(session: AsyncSession) -> DefaultJobSearchCommandService:
    return DefaultJobSearchCommandService(
        job_provider=get_job_provider(),
        job_offer_repository=SQLAlchemyJobOfferRepository(session),
        favorite_job_repository=SQLAlchemyFavoriteJobRepository(session),
        commit=session.commit,
    )


def get_job_search_query_service(session: AsyncSession) -> DefaultJobSearchQueryService:
    return DefaultJobSearchQueryService(
        job_offer_repository=SQLAlchemyJobOfferRepository(session),
        favorite_job_repository=SQLAlchemyFavoriteJobRepository(session),
    )
