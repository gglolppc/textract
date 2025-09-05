from contextlib import asynccontextmanager

import cv2
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core import model
from app.utils.limiter import limiter
from app.config import settings
from app.routers import upload, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not model.EAST_MODEL.exists():
        raise FileNotFoundError("Нет модели EAST")

    model.net = cv2.dnn.readNet(str(model.EAST_MODEL))
    print("✅ EAST модель загружена")

    yield

    model.net = None
    print("🛑 EAST модель выгружена")

app = FastAPI(lifespan=lifespan, title="textract")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])

