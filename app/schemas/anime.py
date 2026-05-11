from datetime import datetime
from pydantic import BaseModel, Field

from app.models.anime import WatchStatus


# ── User anime list entries ───────────────────────────────────────────────────
class EntryCreate(BaseModel):
    mal_id: str = Field(description="MyAnimeList ID — we'll fetch and cache the anime if needed")
    status: WatchStatus
    rating: int | None = Field(default=None, ge=1, le=10)
    episodes_watched: int | None = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class EntryUpdate(BaseModel):
    status: WatchStatus
    rating: int | None = Field(default=None, ge=1, le=10)
    episodes_watched: int | None = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


# Responses
class AnimeResponse(BaseModel):
    id: int
    mal_id: int
    title_original: str
    title_english: str | None
    image_url: str | None
    genre: str | None
    theme: str | None
    prequel: str | None
    sequel: str | None
    episodes: int | None
    date_start_emission: datetime | None
    date_end_emission: datetime | None
    synopsis: str | None
    score: float | None
    age: str | None
    status: str | None

    model_config = {"from_attributes": True}

    
class EntryResponse(BaseModel):
    id: int
    status: WatchStatus
    rating: int | None
    episodes_watched: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    anime: AnimeResponse

    model_config = {"from_attributes": True}




