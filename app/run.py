"""
FastAPI application entry.

Mounts scraper routes so each site type has its own endpoint.
"""
import logging
from fastapi import FastAPI

from app.routes.angular_route import router as Angular_Router
from app.routes.chat_route import router as Chat_Router
# from app.routes.react_route import router as React_Router
# from app.routes.static_route import router as Static_Router
# from app.routes.woocommerce_route import router as Wordpress_Router
# from app.routes.static_wordpress_route import router as Static_Wordpress_Router

from app.utils.configs_parser import ConfigsParser

APP_CONFIGS = ConfigsParser.parser('APP')
logging_level = getattr(
    logging, APP_CONFIGS['logging_level']
)

logging.basicConfig(
    level=logging_level,
    format='%(asctime)s] - %(name)s - %(levelname)s in %(module)s:%(lineno)d:%(funcName)-10s %(message)s',
    force=True
)

log = logging.getLogger(__name__)
log.info("Starting Chatbot application")
app = FastAPI(
    title="Chatbot Scraper Service",
    description="Dedicated scrape endpoints per site engine (static, React, Angular, WooCommerce).",
    version="0.1.0",
)

log.info("Mounting routers")
app.include_router(Angular_Router)
app.include_router(Chat_Router)
# app.include_router(React_Router)
# app.include_router(Static_Router)
# app.include_router(Wordpress_Router)
# app.include_router(Static_Wordpress_Router)

@app.get("/health")
def health():
    return {"status": "ok"}
log.info("Application started successfully...")