from abc import ABC, abstractmethod

from app.domain.model.aggregates.job_offer import JobOffer


class JobOfferRepository(ABC):
    @abstractmethod
    async def upsert_many(self, offers: list[JobOffer]) -> list[JobOffer]: ...

    @abstractmethod
    async def find_by_id(self, job_offer_id: int) -> JobOffer | None: ...
