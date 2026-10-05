from datetime import datetime, timezone

import pytest

from app.application.internal.command_services.default_job_search_command_service import (
    DefaultJobSearchCommandService,
)
from app.application.ports.job_provider import ProviderUnavailable
from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.model.commands.search_jobs_command import SearchJobsCommand


def build_offer() -> JobOffer:
    return JobOffer(
        id=None,
        provider="jooble_pe",
        external_id="external-1",
        title="Developer",
        company=None,
        location="Lima",
        description_snippet=None,
        salary=None,
        employment_type=None,
        source=None,
        external_url="https://pe.jooble.com/job/1",
        provider_updated_at=None,
        last_seen_at=datetime(2026, 9, 30, 9, 0, tzinfo=timezone.utc),
    )


class AvailableProvider:
    def __init__(self, total: int) -> None:
        self.total = total

    async def search(self, **_):
        return [build_offer()], self.total


class UnavailableProvider:
    async def search(self, **_):
        raise ProviderUnavailable()


class OfferRepositorySpy:
    def __init__(self) -> None:
        self.upserted: list[list[JobOffer]] = []

    async def upsert_many(self, offers):
        self.upserted.append(offers)
        return offers

    async def find_by_id(self, job_offer_id):
        return None


class FavoriteRepositoryStub:
    async def add(self, favorite_job):
        return True

    async def remove(self, user_id, job_offer_id):
        return True

    async def list_for_user(self, user_id, offset, limit):
        return [], 0


class CommitSpy:
    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self):
        self.calls += 1


def build_command(page_size: int = 10) -> SearchJobsCommand:
    return SearchJobsCommand(
        keywords="python",
        location="Lima",
        page=1,
        page_size=page_size,
        radius_km=0,
    )


@pytest.mark.asyncio
async def test_search_total_is_capped_to_the_browsable_pages():
    # Arrange
    repository = OfferRepositorySpy()
    commit = CommitSpy()
    service = DefaultJobSearchCommandService(
        job_provider=AvailableProvider(total=87),
        job_offer_repository=repository,
        favorite_job_repository=FavoriteRepositoryStub(),
        commit=commit,
    )

    # Act
    offers, total, provider_status = await service.handle_search(build_command(page_size=10))

    # Assert
    assert total == 30
    assert provider_status == "available"
    assert len(offers) == 1
    assert len(repository.upserted) == 1
    assert commit.calls == 1


@pytest.mark.asyncio
async def test_search_reports_unavailable_without_persisting_anything():
    # Arrange
    repository = OfferRepositorySpy()
    commit = CommitSpy()
    service = DefaultJobSearchCommandService(
        job_provider=UnavailableProvider(),
        job_offer_repository=repository,
        favorite_job_repository=FavoriteRepositoryStub(),
        commit=commit,
    )

    # Act
    offers, total, provider_status = await service.handle_search(build_command())

    # Assert
    assert (offers, total, provider_status) == ([], 0, "unavailable")
    assert repository.upserted == []
    assert commit.calls == 0
