from fastapi import APIRouter
from .auth import router as auth_router
from .artwork import router as artwork_router
from .blockchain import router as blockchain_router
from .admin import router as admin_router  
router = APIRouter()

# Include all versioned routers
router.include_router(auth_router)
router.include_router(artwork_router)
router.include_router(blockchain_router)
router.include_router(admin_router)  
