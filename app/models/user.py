from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime

from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "user"

    id:Mapped[int] = mapped_column(primary_key=True)
    username:Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email:Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password:Mapped[str] = mapped_column(String(255), nullable=False)
    is_active:Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    ) 

    # Relationship - an user has many anime entries
    anime_list:Mapped[list["UserAnimeEntry"]] = relationship("UserAnimeEntry", back_populates="user", cascade="all, delete-orphan")
