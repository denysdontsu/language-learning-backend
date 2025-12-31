from app.core.config import settings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url='/docs' if settings.is_development else None
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
    return {
        'message': settings.DESCRIPTION,
        'docs': '/doss' if settings.is_development else None,
        'version': settings.VERSION
    }

@app.get('/health')
async def health_check():
    return {'status': 'healthy'}
