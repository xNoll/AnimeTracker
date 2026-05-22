from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.anime import AnimeResponse

router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("/search", response_model=list[AnimeResponse])
async def search_anime(
    q: str = Query(min_length=2, description="Search query (e.g. 'Fullmetal Alchemist')"),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    """
    Search anime via Jikan (MyAnimeList API).
    Results are cached locally so repeated searches don't hit external API.
    """
    raw_results = await crud.anime.search_jikan(q, page)
    if not raw_results:
        return []

    # Cache each result we haven't seen yet
    anime_list = []
    for item in raw_results:
        anime = crud.anime.upsert_anime(db, item["mal_id"], item)
        anime_list.append(anime)

    return anime_list


@router.get("/browse", response_model=list[AnimeResponse])
def browse_cached(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Browse the locally cached anime, sorted by score.
    This doesn't call Jikan — it's your own DB.
    """
    return crud.anime.list_anime(db, skip=skip, limit=limit)


@router.get("/{mal_id}", response_model=AnimeResponse)
async def get_anime(mal_id: int, db: Session = Depends(get_db)):
    """
    Get a specific anime by MAL ID.
    Returns cached version if available; fetches from Jikan otherwise.
    """
    anime = crud.anime.get_anime_by_mal_id(db, mal_id)
    if not anime:
        data = await crud.anime.fetch_jikan_by_id(mal_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Anime with MAL ID {mal_id} not found",
            )
        anime = crud.anime.upsert_anime(db, mal_id, data)
    return anime
