from contextlib import asynccontextmanager

import cv2
from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.core import model
from app.utils.security.limiter import limiter
from app.config.config import settings
from app.routers import upload, health, feedback, billing, account, index, admin, pdf, pages, tts
from app.routers.auth import auth, google_auth
from app.routers.pages import api_router

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
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,  # придумай любой длинный ключ
    same_site="lax",
    https_only=True  # можно False для локальной разработки
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later. Limit 5 requests per hour."}
    )

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
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(auth.router)
app.include_router(google_auth.router)
app.include_router(billing.router)
app.include_router(account.router)
app.include_router(index.router)
app.include_router(admin.router)
app.include_router(pdf.router)
app.include_router(pages.router)
app.include_router(api_router)
app.include_router(tts.router)


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    return FileResponse("app/static/seo/robots.txt", media_type="text/plain")

@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    return FileResponse("app/static/seo/sitemap.xml", media_type="application/xml")
