from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.model.aggregates.job_offer import JobOffer
from app.interfaces.rest.controller import job_search_controller
from app.interfaces.rest.controller.job_search_controller import router as jobs_router

SEEN_AT = datetime(2026, 9, 30, 9, 0, tzinfo=timezone.utc)

STORED_OFFER = JobOffer(
    id=42,
    provider="jooble_pe",
    external_id="external-42",
    title="Backend Developer",
    company="Acme",
    location="Lima",
    description_snippet="Python y FastAPI",
    salary=None,
    employment_type="full-time",
    source="jooble",
    external_url="https://pe.jooble.com/job/42",
    provider_updated_at=None,
    last_seen_at=SEEN_AT,
)


class JobQueryServiceStub:
    async def handle_get_job_by_id(self, query):
        return STORED_OFFER if query.job_offer_id == 42 else None


def build_client() -> TestClient:
    app = FastAPI()
    app.include_router(jobs_router)

    async def fake_session():
        yield object()

    app.dependency_overrides[job_search_controller.get_db_session] = fake_session
    app.dependency_overrides[job_search_controller.get_current_user_id] = lambda: 1
    job_search_controller.get_job_search_query_service = lambda _session: JobQueryServiceStub()
    return TestClient(app)


def test_get_job_returns_the_normalized_offer():
    # Arrange
    client = build_client()

    # Act
    response = client.get("/api/v1/jobs/42")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 42
    assert body["title"] == "Backend Developer"
    assert body["company"] == "Acme"
    assert body["external_url"] == "https://pe.jooble.com/job/42"


def test_get_job_returns_404_for_an_unknown_offer():
    # Arrange
    client = build_client()

    # Act
    response = client.get("/api/v1/jobs/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Job offer not found."
