from dataclasses import dataclass


@dataclass(frozen=True)
class SearchJobsCommand:
    keywords: str
    location: str
    page: int
    page_size: int
    radius_km: int
