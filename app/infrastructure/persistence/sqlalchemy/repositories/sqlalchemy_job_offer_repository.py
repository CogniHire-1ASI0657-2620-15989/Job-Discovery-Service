from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.repositories.job_offer_repository import JobOfferRepository
from app.infrastructure.persistence.sqlalchemy.models.job_offer_model import JobOfferModel


class SQLAlchemyJobOfferRepository(JobOfferRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert_many(self, offers: list[JobOffer]) -> list[JobOffer]:
        persisted: list[JobOffer] = []
        for offer in offers:
            model = await self._session.scalar(
                select(JobOfferModel).where(
                    JobOfferModel.provider == offer.provider,
                    JobOfferModel.external_id == offer.external_id,
                )
            )
            if model is None:
                model = JobOfferModel(
                    provider=offer.provider,
                    external_id=offer.external_id,
                    title=offer.title,
                    company=offer.company,
                    location=offer.location,
                    description_snippet=offer.description_snippet,
                    salary=offer.salary,
                    employment_type=offer.employment_type,
                    source=offer.source,
                    external_url=offer.external_url,
                    provider_updated_at=offer.provider_updated_at,
                    last_seen_at=offer.last_seen_at,
                )
                self._session.add(model)
            else:
                model.title = offer.title
                model.company = offer.company
                model.location = offer.location
                model.description_snippet = offer.description_snippet
                model.salary = offer.salary
                model.employment_type = offer.employment_type
                model.source = offer.source
                model.external_url = offer.external_url
                model.provider_updated_at = offer.provider_updated_at
                model.last_seen_at = offer.last_seen_at
            await self._session.flush()
            persisted.append(self._to_domain(model))
        return persisted

    async def find_by_id(self, job_offer_id: int) -> JobOffer | None:
        model = await self._session.get(JobOfferModel, job_offer_id)
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_domain(model: JobOfferModel) -> JobOffer:
        return JobOffer(
            id=model.id,
            provider=model.provider,
            external_id=model.external_id,
            title=model.title,
            company=model.company,
            location=model.location,
            description_snippet=model.description_snippet,
            salary=model.salary,
            employment_type=model.employment_type,
            source=model.source,
            external_url=model.external_url,
            provider_updated_at=model.provider_updated_at,
            last_seen_at=model.last_seen_at,
        )
