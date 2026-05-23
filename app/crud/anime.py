from app.config import settings
from app.schemas.anime import EntryCreate, EntryUpdate
from app.models.anime import WatchStatus, UserAnimeEntry, Anime

import httpx
from datetime import datetime, timezone
from sqlalchemy.orm import Session



# ── Jikan API helpers ─────────────────────────────────────────────────────────
async def search_jikan(query: str, page: int = 1) -> list[dict]:
    """Call Jikan search API. Returns raw list of anime dicts."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.jikan_api_url}/anime",
            params={"q": query, "page": page, "limit": 20, "sfw": True},
            timeout=10.0,
        )
        resp.raise_for_status()

        return resp.json().get("data", [])
    

def _get_aired_from_data(data: dict) -> datetime | None:
    aired_from = None
    if data.get("aired", {}).get("from"):
        try:
            aired_from = datetime.fromisoformat(
                data["aired"]["from"].replace("Z", "+00:00")
            )
        except (TypeError, ValueError):
            pass
    
    return aired_from


def _get_aired_to_data(data: dict) -> datetime | None:
    aired_to = None
    if data.get("aired", {}).get("to"):
        try:
            aired_to = datetime.fromisoformat(
                data["aired"]["to"].replace("Z", "+00:00")
            )
        except (TypeError, ValueError):
            pass
    
    return aired_to
    

def _parse_jikan_anime_data(data: dict) -> dict:
    """Extract only what we need from a Jikan anime object."""
    themes = data.get("themes", [])
    genres = data.get("genres", [])

    return{
        "mal_id": data["mal_id"],
        "title_original": data["title"],
        "title_english": data.get("title_english"),
        "synopsis": data.get("synopsis"),
        "image_url": data.get("images", {}).get("jpg", {}).get("image_url"),
        "episodes": data.get("episodes"),
        "score": data.get("score"),
        "status": data.get("status"),
        "age": data.get("rating"),
        "theme": ", ".join(t["name"] for t in themes) if themes else None,
        "genre": genres[0]["name"] if genres else None,
        "date_start_emission": _get_aired_from_data(data),
        "date_end_emission": _get_aired_to_data(data),
    }


async def fetch_jikan_by_id(mal_id: int) -> dict | None:
    """Fetch a single anime from Jikan by MAL ID."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.jikan_api_url}/anime/{mal_id}",
            timeout=10.0,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

        return resp.json().get("data")


# ── Anime DB helpers ──────────────────────────────────────────────────────────

def get_anime_by_mal_id(db: Session, mal_id: int) -> Anime | None:
    return db.query(Anime).filter(Anime.mal_id == mal_id).first()


def list_anime(db: Session, skip: int = 0, limit: int = 20) -> list[Anime]:
    return db.query(Anime).order_by(Anime.score.desc().nullslast()).offset(skip).limit(limit).all()


def upsert_anime(db: Session, mal_id: int, jikan_data: dict) -> Anime:
    """Create or update an anime from Jikan data."""
    parsed = _parse_jikan_anime_data(jikan_data)
    anime = get_anime_by_mal_id(db, mal_id)

    if anime:
        for key, value in parsed.items():
            setattr(anime, key, value)                  
        anime.cached_at = datetime.now(timezone.utc)
    else:
        anime = Anime(**parsed) # Parse and send values as a dict.
        db.add(anime)

    db.commit()
    db.refresh(anime)
    return anime


# ── User list entries ─────────────────────────────────────────────────────────

def get_user_entries(db: Session, user_id: int) -> list[UserAnimeEntry]:
    """
        Get all entries for an user, ordered by the most recent/updated one.
    """
    return (
        db.query(UserAnimeEntry)
        .filter(UserAnimeEntry.user_id == user_id)
        .order_by(UserAnimeEntry.updated_at.desc())
        .all()
    )


def get_user_entry(db: Session, user_id: int, anime_id: int) -> UserAnimeEntry | None:
    """
        Return the entry if exists.
    """
    return (
        db.query(UserAnimeEntry)
        .filter(UserAnimeEntry.user_id == user_id, UserAnimeEntry.anime_id == anime_id)
        .first()
    )


def create_entry(db: Session, user_id: int, anime: Anime, data: EntryCreate) -> UserAnimeEntry:
    entry = UserAnimeEntry(
        user_id = user_id,
        anime_id = anime.id,
        status = data.status,
        rating = data.rating,
        episodes_watched = data.episodes_watched,
        notes = data.notes
    )
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except Exception:
        db.rollback()   
        raise


def update_entry(db: Session, entry: UserAnimeEntry, data: EntryUpdate) -> UserAnimeEntry:
    update_data = data.model_dump(exclude_unset=True)  # only update provided fields
    for key, value in update_data.items():
        setattr(entry, key, value)
    entry.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(entry)

    return entry


def delete_entry(db: Session, entry: UserAnimeEntry) -> None:
    db.delete(entry)
    db.commit()
    #db.refresh()


def filter_entries_by_status(db: Session, user_id: int, status: WatchStatus) -> list[UserAnimeEntry]:
    return (
        db.query(UserAnimeEntry)
        .filter(UserAnimeEntry.user_id == user_id, UserAnimeEntry.status == status)
        .all()
    )    