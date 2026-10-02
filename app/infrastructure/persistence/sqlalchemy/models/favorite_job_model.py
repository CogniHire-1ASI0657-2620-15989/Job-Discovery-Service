from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.sqlalchemy.database import Base


class FavoriteJobModel(Base):
    __tablename__ = "favorite_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_offer_id", name="uq_favorite_user_offer"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    job_offer_id: Mapped[int] = mapped_column(ForeignKey("job_offers.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
