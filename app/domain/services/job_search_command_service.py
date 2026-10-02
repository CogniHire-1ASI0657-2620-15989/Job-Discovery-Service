from abc import ABC, abstractmethod

from app.domain.model.commands.add_favorite_job_command import AddFavoriteJobCommand
from app.domain.model.commands.remove_favorite_job_command import RemoveFavoriteJobCommand
from app.domain.model.commands.search_jobs_command import SearchJobsCommand
from app.domain.model.aggregates.job_offer import JobOffer


class JobSearchCommandService(ABC):
    @abstractmethod
    async def handle_search(self, command: SearchJobsCommand) -> tuple[list[JobOffer], int, str]: ...

    @abstractmethod
    async def handle_add_favorite(self, command: AddFavoriteJobCommand) -> tuple[JobOffer | None, bool]: ...

    @abstractmethod
    async def handle_remove_favorite(self, command: RemoveFavoriteJobCommand) -> bool: ...
