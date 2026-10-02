from datetime import datetime

from pydantic import BaseModel, HttpUrl


class JobResource(BaseModel):
    id: int
    provider: str
    title: str
    company: str | None = None
    location: str | None = None
    description_snippet: str | None = None
    salary: str | None = None
    employment_type: str | None = None
    source: str | None = None
    external_url: HttpUrl
    provider_updated_at: datetime | None = None
