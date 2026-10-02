from datetime import datetime, timezone

import pytest

from app.application.internal.command_services.default_job_search_command_service import DefaultJobSearchCommandService
from app.application.internal.query_service.default_job_search_query_service import DefaultJobSearchQueryService
from app.application.ports.job_provider import ProviderUnavailable
from app.domain.model.commands.add_favorite_job_command import AddFavoriteJobCommand
from app.domain.model.commands.search_jobs_command import SearchJobsCommand
from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.model.queries.get_favorite_jobs_query import GetFavoriteJobsQuery


def offer(offer_id: int | None = 1) -> JobOffer:
    return JobOffer(offer_id, "jooble_pe", "external-1", "Developer", None, "Lima", None, None, None, None, "https://example.test/job", None, datetime.now(timezone.utc))


class UnavailableProvider:
    async def search(self, **_: object):
        raise ProviderUnavailable()


class AvailableProvider:
    async def search(self, **_: object):
        return [offer()], 500


class OfferRepository:
    def __init__(self):
        self.item = offer()

    async def upsert_many(self, offers):
        return [offer(index + 1) for index, _ in enumerate(offers)]

    async def find_by_id(self, job_offer_id):
        return self.item if job_offer_id == 1 else None


class FavoriteRepository:
    def __init__(self):
        self.favorites: set[tuple[int, int]] = set()

    async def add(self, favorite_job):
        key = (favorite_job.user_id, favorite_job.job_offer_id)
        if key in self.favorites:
            return False
        self.favorites.add(key)
        return True

    async def remove(self, user_id, job_offer_id):
        key = (user_id, job_offer_id)
        if key not in self.favorites:
            return False
        self.favorites.remove(key)
        return True

    async def list_for_user(self, user_id, offset, limit):
        return [], 0


async def commit():
    return None


@pytest.mark.asyncio
async def test_unavailable_provider_returns_empty_contract():
    service = DefaultJobSearchCommandService(UnavailableProvider(), OfferRepository(), FavoriteRepository(), commit)
    offers, total, provider_status = await service.handle_search(
        SearchJobsCommand(keywords="python", location="Lima", page=1, page_size=20, radius_km=0)
    )
    assert offers == []
    assert total == 0
    assert provider_status == "unavailable"


@pytest.mark.asyncio
async def test_search_total_is_limited_to_browsable_pages():
    service = DefaultJobSearchCommandService(AvailableProvider(), OfferRepository(), FavoriteRepository(), commit)

    _, default_total, _ = await service.handle_search(
        SearchJobsCommand(keywords="python", location="Lima", page=1, page_size=10, radius_km=0)
    )
    _, maximum_total, _ = await service.handle_search(
        SearchJobsCommand(keywords="python", location="Lima", page=1, page_size=20, radius_km=0)
    )

    assert default_total == 30
    assert maximum_total == 60


@pytest.mark.asyncio
async def test_favorites_are_idempotent_and_user_scoped():
    favorites = FavoriteRepository()
    service = DefaultJobSearchCommandService(UnavailableProvider(), OfferRepository(), favorites, commit)
    saved, created = await service.handle_add_favorite(AddFavoriteJobCommand(1, 1))
    _, repeated = await service.handle_add_favorite(AddFavoriteJobCommand(1, 1))
    _, other_user = await service.handle_add_favorite(AddFavoriteJobCommand(2, 1))
    assert saved is not None
    assert created is True
    assert repeated is False
    assert other_user is True


@pytest.mark.asyncio
async def test_favorites_query_uses_page_offset():
    query_service = DefaultJobSearchQueryService(OfferRepository(), FavoriteRepository())
    offers, total = await query_service.handle_get_favorites(GetFavoriteJobsQuery(user_id=1, page=2, page_size=20))
    assert offers == []
    assert total == 0
