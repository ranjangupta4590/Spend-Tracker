import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import expenses, summary, auth

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("spend_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized successfully.")
    yield


app = FastAPI(
    title="Spend Tracker API",
    description="Secure, production-grade expense tracking API with JWT authentication and analytics.",
    version="1.0.0",
    lifespan=lifespan,
)

# Global safe error handling to prevent leaking internal stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception processing %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


# Request body size limiter middleware
@app.middleware("http")
async def check_content_length(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > settings.max_body_size_bytes:
                return JSONResponse(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    content={"detail": "Request payload exceeds allowed maximum size."},
                )
        except ValueError:
            pass
    return await call_next(request)


# Rate limit middleware
app.add_middleware(RateLimitMiddleware)

# CORS configuration from environment settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(summary.router)


@app.get("/health", summary="Health check", tags=["health"])
def health_check():
    return {"status": "ok"}


# Frontend static files & HTML routes
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_dashboard():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse(status_code=404, content={"message": "Frontend not found"})

    @app.get("/login", include_in_schema=False)
    def serve_login():
        login_file = frontend_dir / "login.html"
        if login_file.exists():
            return FileResponse(login_file)
        return JSONResponse(status_code=404, content={"message": "Login page not found"})

    @app.get("/signup", include_in_schema=False)
    def serve_signup():
        signup_file = frontend_dir / "signup.html"
        if signup_file.exists():
            return FileResponse(signup_file)
        return JSONResponse(status_code=404, content={"message": "Signup page not found"})

    @app.get("/verify", include_in_schema=False)
    def serve_verify():
        verify_file = frontend_dir / "verify.html"
        if verify_file.exists():
            return FileResponse(verify_file)
        return JSONResponse(status_code=404, content={"message": "Verification page not found"})
