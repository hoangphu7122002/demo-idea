from fastapi import FastAPI

from app.api.routes import chat, health, jobs, notes, posts, suggestions
from app.core.settings import get_settings

app = FastAPI(title=f"{get_settings().app_name} API", version="0.1.0")
app.include_router(health.router)
app.include_router(notes.router)
app.include_router(jobs.router)
app.include_router(chat.router)
app.include_router(posts.router)
app.include_router(suggestions.router)
app.include_router(suggestions.filter_router)
app.include_router(suggestions.approve_router)
