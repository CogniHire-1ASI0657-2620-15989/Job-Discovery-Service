from dataclasses import dataclass


@dataclass(frozen=True)
class GetFavoriteJobsQuery:
    user_id: int
    page: int
    page_size: int
