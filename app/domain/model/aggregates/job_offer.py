from dataclasses import dataclass
from datetime import datetime


@dataclass
class JobOffer:
    """Aggregate root for a normalized job offer stored by Job-Search."""

    id: int | None
    provider: str
    external_id: str
    title: str
    company: str | None
    location: str | None
    description_snippet: str | None
    salary: str | None
    employment_type: str | None
    source: str | None
    external_url: str
    provider_updated_at: datetime | None
    last_seen_at: datetime

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.external_id.strip():
            raise ValueError("El proveedor y el identificador externo son obligatorios.")
        if not self.title.strip() or not self.external_url.strip():
            raise ValueError("El título y el enlace externo son obligatorios.")
