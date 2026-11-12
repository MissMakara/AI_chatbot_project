"""
Per-scraper FastAPI routes.

Each endpoint binds to exactly one scraper strategy so callers cannot
accidentally run the wrong engine for a site type.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.schemas.responses import ScrapeResponse

"""
This acts as a central controller and error-handler for all web scraping tasks.

"""
def _run(scraper_name: str, scrape_fn, url: HttpUrl) -> ScrapeResponse:
    try:
        text = scrape_fn(str(url))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"{scraper_name} failed: {exc}") from exc

    return ScrapeResponse(scraper=scraper_name, url=str(url), text=text)




