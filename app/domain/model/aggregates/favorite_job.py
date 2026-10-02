from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FavoriteJob:
    """Aggregate root for a user's saved job reference."""

    user_id: int
    job_offer_id: int
    created_at: datetime

    def __post_init__(self) -> None:
        if self.user_id <= 0 or self.job_offer_id <= 0:
            raise ValueError("El usuario y la oferta favorita deben ser válidos.")
