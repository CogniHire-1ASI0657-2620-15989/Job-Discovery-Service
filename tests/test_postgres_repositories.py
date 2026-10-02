import os
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.domain.model.aggregates.job_offer import JobOffer
from app.domain.model.aggregates.favorite_job import FavoriteJob
from app.infrastructure.persistence.sqlalchemy.database import Base
from app.infrastructure.persistence.sqlalchemy.models import favorite_job_model, job_offer_model  # noqa: F401
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_favorite_job_repository import SQLAlchemyFavoriteJobRepository
from app.infrastructure.persistence.sqlalchemy.repositories.sqlalchemy_job_offer_repository import SQLAlchemyJobOfferRepository


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="Set TEST_DATABASE_URL to run PostgreSQL repository integration tests.")


@pytest.mark.asyncio
async def test_offer_snapshot_and_favorite_are_isolated_by_user():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        offers = SQLAlchemyJobOfferRepository(session)
        favorites = SQLAlchemyFavoriteJobRepository(session)
        saved = (await offers.upsert_many([JobOffer(
            None, "jooble_pe", "integration-1", "Developer", "Acme", "Lima", "Python", None,
            None, None, "https://example.test/job", None, datetime.now(timezone.utc),
        )]))[0]
        await favorites.add(FavoriteJob(user_id=100, job_offer_id=saved.id, created_at=datetime.now(timezone.utc)))
        await session.commit()
        mine, mine_total = await favorites.list_for_user(100, 0, 20)
        other, other_total = await favorites.list_for_user(200, 0, 20)
        assert mine_total == 1 and mine[0].title == "Developer"
        assert other_total == 0 and other == []
    await engine.dispose()
