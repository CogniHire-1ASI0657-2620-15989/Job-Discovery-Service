from datetime import datetime, timezone

import httpx

from app.application.ports.job_provider import JobProvider, ProviderUnavailable
from app.domain.model.aggregates.job_offer import JobOffer
from app.infrastructure.providers.circuit_breaker import CircuitBreaker


class JooblePeruProvider(JobProvider):
    provider_name = "jooble_pe"

    def __init__(self, api_key: str, base_url: str, client: httpx.AsyncClient | None = None, breaker: CircuitBreaker | None = None):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = client
        self._breaker = breaker or CircuitBreaker()

    async def search(self, *, keywords: str, location: str, page: int, page_size: int, radius_km: int) -> tuple[list[JobOffer], int]:
        if not self._breaker.allow_request():
            raise ProviderUnavailable("Jooble circuit breaker is open.")

        payload = {
            "keywords": keywords,
            "location": location,
            "radius": str(radius_km),
            "page": str(page),
            "ResultOnPage": str(page_size),
            "companysearch": False,
        }
        try:
            if self._client is not None:
                response = await self._client.post(f"{self._base_url}/{self._api_key}", json=payload)
            else:
                timeout = httpx.Timeout(0.7)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(f"{self._base_url}/{self._api_key}", json=payload)
            response.raise_for_status()
            body = response.json()
            jobs = [self._normalize(job) for job in body.get("jobs", [])]
            self._breaker.record_success()
            return jobs, int(body.get("totalCount", len(jobs)))
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            self._breaker.record_failure()
            raise ProviderUnavailable("Jooble is currently unavailable.") from exc

    def _normalize(self, raw: dict) -> JobOffer:
        external_id = str(raw.get("id", "")).strip()
        title = str(raw.get("title", "")).strip()
        external_url = str(raw.get("link", "")).strip()
        if not external_id or not title or not external_url:
            raise ValueError("Jooble returned an incomplete job offer.")
        return JobOffer(
            id=None,
            provider=self.provider_name,
            external_id=external_id,
            title=title,
            company=self._optional_string(raw.get("company")),
            location=self._optional_string(raw.get("location")),
            description_snippet=self._optional_string(raw.get("snippet")),
            salary=self._optional_string(raw.get("salary")),
            employment_type=self._optional_string(raw.get("type")),
            source=self._optional_string(raw.get("source")),
            external_url=external_url,
            provider_updated_at=self._parse_datetime(raw.get("updated")),
            last_seen_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _optional_string(value: object) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None

    @staticmethod
    def _parse_datetime(value: object) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
