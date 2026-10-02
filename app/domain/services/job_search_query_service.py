from abc import ABC, abstractmethod

from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.model.queries.get_favorite_jobs_query import GetFavoriteJobsQuery
from app.domain.model.queries.get_job_by_id_query import GetJobByIdQuery


class JobSearchQueryService(ABC):
    @abstractmethod
    async def handle_get_job_by_id(self, query: GetJobByIdQuery) -> JobOffer | None: ...

    @abstractmethod
    async def handle_get_favorites(self, query: GetFavoriteJobsQuery) -> tuple[list[JobOffer], int]: ...
