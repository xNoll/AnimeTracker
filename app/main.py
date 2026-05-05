from fastapi import FastAPI

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
