from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.model.aggregates.favorite_job import FavoriteJob
from app.domain.repositories.favorite_job_repository import FavoriteJobRepository
from app.infrastructure.persistence.sqlalchemy.models.favorite_job_model import FavoriteJobModel
from app.infrastructure.persistence.sqlalchemy.models.job_offer_model import JobOfferModel
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_job_offer_repository import SQLAlchemyJobOfferRepository


class SQLAlchemyFavoriteJobRepository(FavoriteJobRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, favorite_job: FavoriteJob) -> bool:
        existing = await self._session.scalar(
            select(FavoriteJobModel.id).where(
                FavoriteJobModel.user_id == favorite_job.user_id,
                FavoriteJobModel.job_offer_id == favorite_job.job_offer_id,
            )
        )
        if existing is not None:
            return False
        self._session.add(
            FavoriteJobModel(
                user_id=favorite_job.user_id,
                job_offer_id=favorite_job.job_offer_id,
                created_at=favorite_job.created_at,
            )
        )
        await self._session.flush()
        return True

    async def remove(self, user_id: int, job_offer_id: int) -> bool:
        favorite = await self._session.scalar(
            select(FavoriteJobModel).where(
                FavoriteJobModel.user_id == user_id,
                FavoriteJobModel.job_offer_id == job_offer_id,
            )
        )
        if favorite is None:
            return False
        await self._session.delete(favorite)
        await self._session.flush()
        return True

    async def list_for_user(self, user_id: int, offset: int, limit: int) -> tuple[list[JobOffer], int]:
        count = await self._session.scalar(
            select(func.count()).select_from(FavoriteJobModel).where(FavoriteJobModel.user_id == user_id)
        )
        models = (await self._session.scalars(
            select(JobOfferModel)
            .join(FavoriteJobModel, FavoriteJobModel.job_offer_id == JobOfferModel.id)
            .where(FavoriteJobModel.user_id == user_id)
            .order_by(FavoriteJobModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )).all()
        return [SQLAlchemyJobOfferRepository._to_domain(model) for model in models], int(count or 0)
