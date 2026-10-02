from enum import IntEnum

from pydantic import BaseModel, Field


class RadiusKm(IntEnum):
    ZERO = 0
    FOUR = 4
    EIGHT = 8
    SIXTEEN = 16
    TWENTY_SIX = 26
    FORTY = 40
    EIGHTY = 80


class SearchJobsResource(BaseModel):
    keywords: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=200)
    # Jooble's free quota is finite. Keep navigation bounded to three pages.
    page: int = Field(default=1, ge=1, le=3)
    page_size: int = Field(default=10, ge=1, le=20)
    # Query parameters arrive as text. IntEnum accepts values such as "0"
    # while preserving the finite set accepted by Jooble.
    radius_km: RadiusKm = RadiusKm.ZERO
