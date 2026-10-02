from datetime import datetime, timezone

from app.application.ports.job_provider import JobProvider, ProviderUnavailable
from app.domain.model.aggregates.favorite_job import FavoriteJob
from app.domain.model.commands.add_favorite_job_command import AddFavoriteJobCommand
from app.domain.model.commands.remove_favorite_job_command import RemoveFavoriteJobCommand
from app.domain.model.commands.search_jobs_command import SearchJobsCommand
from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.repositories.favorite_job_repository import FavoriteJobRepository
from app.domain.repositories.job_offer_repository import JobOfferRepository
from app.domain.services.job_search_command_service import JobSearchCommandService


class DefaultJobSearchCommandService(JobSearchCommandService):
    MAX_SEARCH_PAGES = 3

    def __init__(self, job_provider: JobProvider, job_offer_repository: JobOfferRepository, favorite_job_repository: FavoriteJobRepository, commit):
        self._job_provider = job_provider
        self._job_offer_repository = job_offer_repository
        self._favorite_job_repository = favorite_job_repository
        self._commit = commit

    async def handle_search(self, command: SearchJobsCommand) -> tuple[list[JobOffer], int, str]:
        try:
            offers, total = await self._job_provider.search(
                keywords=command.keywords, location=command.location, page=command.page,
                page_size=command.page_size, radius_km=command.radius_km,
            )
        except ProviderUnavailable:
            return [], 0, "unavailable"
        persisted_offers = await self._job_offer_repository.upsert_many(offers)
        await self._commit()
        # Do not advertise more results than the public API lets a client browse.
        # This is 30 results with the default page size and at most 60 with size 20.
        visible_total = min(total, command.page_size * self.MAX_SEARCH_PAGES)
        return persisted_offers, visible_total, "available"

    async def handle_add_favorite(self, command: AddFavoriteJobCommand) -> tuple[JobOffer | None, bool]:
        offer = await self._job_offer_repository.find_by_id(command.job_offer_id)
        if offer is None:
            return None, False
        favorite_job = FavoriteJob(
            user_id=command.user_id,
            job_offer_id=command.job_offer_id,
            created_at=datetime.now(timezone.utc),
        )
        created = await self._favorite_job_repository.add(favorite_job)
        if created:
            await self._commit()
        return offer, created

    async def handle_remove_favorite(self, command: RemoveFavoriteJobCommand) -> bool:
        removed = await self._favorite_job_repository.remove(command.user_id, command.job_offer_id)
        if removed:
            await self._commit()
        return removed
