from dataclasses import dataclass


@dataclass(frozen=True)
class AddFavoriteJobCommand:
    user_id: int
    job_offer_id: int
