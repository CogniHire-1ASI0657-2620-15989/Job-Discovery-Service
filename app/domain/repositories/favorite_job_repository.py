from abc import ABC, abstractmethod

from app.domain.model.aggregates.favorite_job import FavoriteJob
from app.domain.model.aggregates.job_offer import JobOffer


class FavoriteJobRepository(ABC):
    @abstractmethod
    async def add(self, favorite_job: FavoriteJob) -> bool: ...

    @abstractmethod
    async def remove(self, user_id: int, job_offer_id: int) -> bool: ...

    @abstractmethod
    async def list_for_user(self, user_id: int, offset: int, limit: int) -> tuple[list[JobOffer], int]: ...
