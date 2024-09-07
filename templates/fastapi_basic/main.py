from functools import lru_cache
from typing import Annotated

import settings
from fastapi import Depends, FastAPI
from routers import item

app = FastAPI(
    docs_url="/",
)


@lru_cache
def get_settings():
    return settings.Settings()


@app.get("/info")
async def info(
    settings: Annotated[settings.Settings, Depends(get_settings)],
):
    return {
        "name": settings.name,
        "version": settings.version,
    }


for router in [
    item.router,
]:
    app.include_router(router)
