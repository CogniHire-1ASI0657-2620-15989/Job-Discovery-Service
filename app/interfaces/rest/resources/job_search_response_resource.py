from pydantic import BaseModel, Field

from app.interfaces.rest.resources.job_resource import JobResource


class JobSearchResponseResource(BaseModel):
    items: list[JobResource]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    provider_status: str
