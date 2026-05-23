from fastapi import FastAPI, HTTPException, Query
from app.config import settings
import httpx

from app.database import Base, engine
from app.models import anime, user  # noqa: F401 — imported so SQLAlchemy registers them
from app.routers import auth, anime as anime_router, list as list_router


# Create tables automatically on startup (fine for dev/SQLite)
# In production with PostgreSQL, use Alembic migrations instead
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    description="A MyAnimeList-inspired API. Track your anime, rate them, manage your list.",
    version="0.2.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc (alternative UI)
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(anime_router.router)
app.include_router(list_router.router)


# Root
@app.get("/", tags=["root"])
def root():
    """Root page."""
    return {
        "Hello": "World"
    }

# Health check
@app.get("/health", tags=["health"])
def health():
    """Used to check if app is up."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "debug": settings.debug
    }


@app.get("/anime/search", tags=["anime"])
async def search_anime(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=25)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.jikan_api_url}/anime", params={"q": q, "limit": limit})

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Error al conectar con Jikan API")

    return [
        {
            "mal_id": anime["mal_id"],
            "title": anime["title"],
            "title_english": anime["title_english"],
            "episodes": anime["episodes"],
            "score": anime["score"],
            "status": anime["status"],
            "image_url": anime["images"]["jpg"]["image_url"],
        }
        for anime in response.json().get("data", [])
    ]

