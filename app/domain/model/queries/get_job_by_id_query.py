from dataclasses import dataclass


@dataclass(frozen=True)
class GetJobByIdQuery:
    job_offer_id: int
