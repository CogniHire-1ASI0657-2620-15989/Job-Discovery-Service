from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.model.queries.get_favorite_jobs_query import GetFavoriteJobsQuery
from app.domain.model.queries.get_job_by_id_query import GetJobByIdQuery
from app.domain.repositories.favorite_job_repository import FavoriteJobRepository
from app.domain.repositories.job_offer_repository import JobOfferRepository
from app.domain.services.job_search_query_service import JobSearchQueryService


class DefaultJobSearchQueryService(JobSearchQueryService):
    def __init__(self, job_offer_repository: JobOfferRepository, favorite_job_repository: FavoriteJobRepository):
        self._job_offer_repository = job_offer_repository
        self._favorite_job_repository = favorite_job_repository

    async def handle_get_job_by_id(self, query: GetJobByIdQuery) -> JobOffer | None:
        return await self._job_offer_repository.find_by_id(query.job_offer_id)

    async def handle_get_favorites(self, query: GetFavoriteJobsQuery) -> tuple[list[JobOffer], int]:
        return await self._favorite_job_repository.list_for_user(
            query.user_id, (query.page - 1) * query.page_size, query.page_size
        )
