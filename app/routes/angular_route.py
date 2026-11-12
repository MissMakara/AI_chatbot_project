import logging

from fastapi import APIRouter, Request

from app.scraper.angular_scraper import main
# from app.schemas.responses import ScrapeResponse
# from app.schemas.requests import ScrapeRequest
# from app.utils.scrape import _run

log = logging.getLogger(__name__)
"""
Calls the scraper
"""

router = APIRouter(
    prefix="/scrape",
    tags=["scrape_routes"]

)

@router.post(
    "/angular",
    summary="Scrape an angular page",
)
async def scrape_angular(body: Request):
    payload = await body.body()
    log.info(f"Received angular request body: {body}")
    return await main (payload)
