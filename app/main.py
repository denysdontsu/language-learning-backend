# Standard library
from contextlib import asynccontextmanager

# Third-party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler # noqa
from slowapi.errors import RateLimitExceeded

# Dependencies
from app.api.dependencies import limiter

# App
from app.api.endpoints import api_router
from app.cache.cache import cache_manager
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await cache_manager.connect()
    yield
    # Shutdown
    await cache_manager.disconnect()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url='/docs' if settings.is_development else None,
    lifespan=lifespan
)

# Rate limiting setup
app.state.limiter = limiter # noqa
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler # noqa
)

if settings.is_development:
    origins = settings.CORS_ORIGINS
else:
    origins = settings.ALLOWED_HOSTS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['*']
)

@app.get('/')
async def root():
    """Root endpoint with API information."""
    return {
        'message': settings.DESCRIPTION,
        'docs': '/doсs' if settings.is_development else None,
        'version': settings.VERSION
    }

@app.get('/health')
async def health_check():
    """Health check endpoint."""
    return {'status': 'healthy'}

# Include routers
app.include_router(api_router)