from abc import ABC, abstractmethod

from app.domain.model.aggregates.job_offer import JobOffer


class ProviderUnavailable(Exception):
    """Raised when an external job provider cannot safely serve a request."""


class JobProvider(ABC):
    @abstractmethod
    async def search(
        self,
        *,
        keywords: str,
        location: str,
        page: int,
        page_size: int,
        radius_km: int,
    ) -> tuple[list[JobOffer], int]: ...
