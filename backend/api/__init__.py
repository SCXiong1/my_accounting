from fastapi import APIRouter

from api.auth import router as auth_router
from api.categories import router as categories_router
from api.statistics import router as statistics_router
from api.tags import router as tags_router
from api.transactions import router as transactions_router
from api.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(tags_router)
api_router.include_router(transactions_router)
api_router.include_router(statistics_router)
