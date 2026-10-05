from datetime import datetime, timezone

import pytest

from app.domain.model.aggregates.job_offer import JobOffer


def build_offer(**overrides) -> JobOffer:
    values = {
        "id": None,
        "provider": "jooble_pe",
        "external_id": "external-1",
        "title": "Developer",
        "company": None,
        "location": "Lima",
        "description_snippet": None,
        "salary": None,
        "employment_type": None,
        "source": None,
        "external_url": "https://pe.jooble.com/job/1",
        "provider_updated_at": None,
        "last_seen_at": datetime(2026, 9, 30, 9, 0, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return JobOffer(**values)


def test_job_offer_accepts_a_complete_offer():
    # Arrange
    provider = "jooble_pe"
    external_id = "external-1"
    title = "Developer"
    external_url = "https://pe.jooble.com/job/1"

    # Act
    offer = build_offer(provider=provider, external_id=external_id, title=title, external_url=external_url)

    # Assert
    assert offer.provider == "jooble_pe"
    assert offer.external_id == "external-1"
    assert offer.title == "Developer"
    assert str(offer.external_url) == external_url


@pytest.mark.parametrize(
    "overrides",
    [
        {"provider": "   "},
        {"external_id": "  "},
        {"title": "   "},
        {"external_url": ""},
    ],
)
def test_job_offer_rejects_missing_mandatory_fields(overrides: dict):
    # Arrange
    incomplete_offer = overrides

    # Act / Assert
    with pytest.raises(ValueError):
        build_offer(**incomplete_offer)
