import httpx
import pytest
import respx

from app.application.ports.job_provider import ProviderUnavailable
from app.infrastructure.providers.circuit_breaker import CircuitBreaker
from app.infrastructure.providers.jooble_peru_provider import JooblePeruProvider


@pytest.mark.asyncio
@respx.mock
async def test_normalizes_jooble_results():
    route = respx.post("https://pe.jooble.org/api/test-key").mock(
        return_value=httpx.Response(200, json={"totalCount": 1, "jobs": [{
            "id": 10, "title": "Backend Developer", "company": "Acme", "location": "Lima",
            "snippet": "Python", "salary": "5000 PEN", "type": "Full-time", "source": "Jooble",
            "link": "https://example.test/job/10", "updated": "2026-09-13T10:00:00Z",
        }]})
    )
    provider = JooblePeruProvider("test-key", "https://pe.jooble.org/api")

    offers, total = await provider.search(keywords="python", location="Lima", page=1, page_size=20, radius_km=0)

    assert route.called
    assert total == 1
    assert offers[0].external_id == "10"
    assert offers[0].provider == "jooble_pe"
    assert offers[0].external_url == "https://example.test/job/10"


@pytest.mark.asyncio
@respx.mock
async def test_opens_circuit_after_three_failures():
    route = respx.post("https://pe.jooble.org/api/test-key").mock(return_value=httpx.Response(503))
    provider = JooblePeruProvider("test-key", "https://pe.jooble.org/api", breaker=CircuitBreaker())

    for _ in range(3):
        with pytest.raises(ProviderUnavailable):
            await provider.search(keywords="python", location="Lima", page=1, page_size=20, radius_km=0)
    with pytest.raises(ProviderUnavailable):
        await provider.search(keywords="python", location="Lima", page=1, page_size=20, radius_km=0)

    assert route.call_count == 3
