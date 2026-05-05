from fastapi import FastAPI, HTTPException, Query
import httpx

app = FastAPI(
    #title=settings.app_name,
    title = "AnimeTracker",
    description="A MyAnimeList-inspired API. Track your anime, rate them, manage your list.",
    version="0.1.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc (alternative UI)
)


# Health check
@app.get("/health", tags=["health"])
def health():
    """Used to check if app is up."""
    return {
        "status": "ok",
        "app": app.title
    }


JIKAN_BASE_URL = "https://api.jikan.moe/v4"


@app.get("/anime/search", tags=["anime"])
async def search_anime(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=25)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{JIKAN_BASE_URL}/anime", params={"q": q, "limit": limit})

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
