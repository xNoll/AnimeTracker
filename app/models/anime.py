from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
        String, DateTime, Integer, Float, Text,
        ForeignKey, UniqueConstraint, Enum
    )
from app.database import Base

from datetime import datetime, timezone
import enum



class WatchStatus(str, enum.Enum):
    plan_to_watch = "plan_to_watch"
    watching = "watching"
    completed = "completed"
    on_hold = "on_hold"
    dropped = "dropped"


class Anime(Base):
    """
    Local cache of anime fetched from Jikan (MyAnimeList).
    We store what we need so we don't hammer the external API on every request.
    """
    __tablename__ = "anime"

    id:Mapped[int] = mapped_column(primary_key=True)
    mal_id:Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title_original:Mapped[str] = mapped_column(String(255), nullable=False)
    title_english:Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url:Mapped[str | None] = mapped_column(String(500), nullable=True)
    genre:Mapped[str | None] = mapped_column(String(50), nullable=True)
    prequel:Mapped[str | None] = mapped_column(String(500), nullable=True)
    sequel:Mapped[str | None] = mapped_column(String(500), nullable=True)
    episodes:Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_start_emission:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_end_emission:Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    synopsis:Mapped[str | None] = mapped_column(Text, nullable=True)
    score:Mapped[float | None] = mapped_column(Float, nullable=True)
    age:Mapped[str | None] = mapped_column(String(3), nullable=True)
    status:Mapped[str | None] = mapped_column(String(20), nullable=True)
    cached_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    entries: Mapped[list["UserAnimeEntry"]] = relationship(
        "UserAnimeEntry", back_populates="anime", cascade="all, delete-orphan"
    )

# A user's personal entry for specific anime in their list
class UserAnimeEntry(Base):
    __tablename__ = "user_anime_entry"
    __table_args__ = (
        UniqueConstraint("user_id", "anime_id", name="uq_user_anime"),  # To avoid duplicity when user adds an anime.
    )

    id:Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"), nullable=False, index=True)
    status: Mapped[WatchStatus] = mapped_column(Enum(WatchStatus), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1–10
    episodes_watched: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships.
    user: Mapped["User"] = relationship("User", back_populates="anime_list")  # noqa: F821
    anime: Mapped["Anime"] = relationship("Anime", back_populates="entries")
