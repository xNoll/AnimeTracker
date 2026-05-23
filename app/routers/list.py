from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.models.anime import WatchStatus
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.anime import EntryCreate, EntryResponse, EntryUpdate

router = APIRouter(prefix="/list", tags=["my list"])


@router.get("/", response_model=list[EntryResponse])
def get_my_list(
    status_filter: WatchStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's anime list. Optionally filter by status."""
    if status_filter:
        return crud.anime.filter_entries_by_status(db, current_user.id, status_filter)
    return crud.anime.get_user_entries(db, current_user.id)


@router.post("/", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def add_to_list(
    data: EntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add an anime to the user's list.
    - If the anime isn't in our DB yet, we fetch it from Jikan and cache it.
    - Prevents duplicates per user.
    """
    # Get or fetch the anime
    anime = crud.anime.get_anime_by_mal_id(db, data.mal_id)
    if not anime:
        jikan_data = await crud.anime.fetch_jikan_by_id(data.mal_id)
        if not jikan_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Anime with MAL ID {data.mal_id} not found on MyAnimeList",
            )
        anime = crud.anime.upsert_anime(db, data.mal_id, jikan_data)

    # Check for duplicate
    existing = crud.anime.get_user_entry(db, current_user.id, anime.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This anime is already in your list. Use PUT to update it.",
        )

    return crud.anime.create_entry(db, current_user.id, anime, data)


@router.put("/{mal_id}", response_model=EntryResponse)
async def update_entry(
    mal_id: int,
    data: EntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update status, rating, progress or notes for an existing list entry."""
    anime = crud.anime.get_anime_by_mal_id(db, mal_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not in local DB")

    entry = crud.anime.get_user_entry(db, current_user.id, anime.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not in your list. Use POST to add it first.",
        )

    return crud.anime.update_entry(db, entry, data)


@router.delete("/{mal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_list(
    mal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an anime from the user's list."""
    anime = crud.anime.get_anime_by_mal_id(db, mal_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")

    entry = crud.anime.get_user_entry(db, current_user.id, anime.id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not in your list")

    crud.anime.delete_entry(db, entry)
