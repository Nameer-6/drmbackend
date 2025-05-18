from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from app.db.database import connect_to_mongo, close_mongo_connection
import os
import logging
import traceback
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(
        title="ART_DRM Backend",
        description="Digital Rights Management for Artworks",
        version="1.0.0"
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handling Middleware
    @app.middleware("http")
    async def db_exception_handler(request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except RuntimeError as e:
            if "MongoDB" in str(e):
                logger.error(f"Database error: {str(e)}")
                return JSONResponse(
                    status_code=503,
                    content={"detail": "Service unavailable - database error"}
                )
            raise
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

    # Register routes and event handlers
    register_routes_and_events(app)

    return app

def register_routes_and_events(app: FastAPI):
    """Register all routes and event handlers"""
    from app.api.v1 import router as api_router
    
    # Database events
    app.add_event_handler("startup", startup_db)
    app.add_event_handler("shutdown", shutdown_db)
    
    # API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Basic routes
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "ART_DRM Backend Service"}
    
    @app.get('/favicon.ico', include_in_schema=False)
    async def favicon():
        return FileResponse(
            os.path.join('static', 'favicon.ico'),
            media_type='image/vnd.microsoft.icon'
        )

async def startup_db():
    """Initialize database connection"""
    try:
        await connect_to_mongo()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {str(e)}")
        raise

async def shutdown_db():
    """Close database connection"""
    await close_mongo_connection()

app = create_app()