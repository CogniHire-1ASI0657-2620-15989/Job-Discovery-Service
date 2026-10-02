from pydantic import BaseModel, Field

from app.interfaces.rest.resources.job_resource import JobResource


class FavoriteMutationResource(BaseModel):
    job: JobResource
    created: bool


class FavoriteListResource(BaseModel):
    items: list[JobResource]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
