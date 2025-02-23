from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI

from app.db.common.db import setup_db
from app.utils.setup_logger import setup_logger

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup mongo database
    await setup_db()
    # setup the logger
    setup_logger()

    yield


app = FastAPI(
    title="Slice Machine Coding Round",
    description="application made during slice machine coding round",
    lifespan=lifespan,
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
