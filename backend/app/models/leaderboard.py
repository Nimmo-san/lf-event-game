from datetime import datetime, timezone

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database import Base


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    game_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
    )

    player_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # marketing_consent: Mapped[bool] = mapped_column(
    #     Boolean,
    #     nullable=False,
    #     default=False,
    # )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )