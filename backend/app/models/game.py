from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database import Base


class GameResult(Base):
    __tablename__ = "game_results"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    player_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    player_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # email: Mapped[str] = mapped_column(
    #     String(255),
    #     nullable=False,
    # )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    lightning_collected: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    duration: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
