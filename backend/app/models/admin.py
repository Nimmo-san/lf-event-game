from datetime import datetime, timezone

from sqlalchemy import Datetime, String

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        Datetime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        Datetime(timezone=True),
        nullable=False,
        index=True,
    )