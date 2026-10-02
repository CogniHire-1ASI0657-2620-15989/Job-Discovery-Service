from dataclasses import dataclass


@dataclass(frozen=True)
class RemoveFavoriteJobCommand:
    user_id: int
    job_offer_id: int
