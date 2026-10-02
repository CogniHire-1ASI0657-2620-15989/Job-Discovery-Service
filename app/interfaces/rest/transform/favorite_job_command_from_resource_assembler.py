from app.domain.model.commands.add_favorite_job_command import AddFavoriteJobCommand
from app.domain.model.commands.remove_favorite_job_command import RemoveFavoriteJobCommand


class FavoriteJobCommandFromResourceAssembler:
    @staticmethod
    def to_add_command(user_id: int, job_offer_id: int) -> AddFavoriteJobCommand:
        return AddFavoriteJobCommand(user_id=user_id, job_offer_id=job_offer_id)

    @staticmethod
    def to_remove_command(user_id: int, job_offer_id: int) -> RemoveFavoriteJobCommand:
        return RemoveFavoriteJobCommand(user_id=user_id, job_offer_id=job_offer_id)
