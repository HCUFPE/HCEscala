from fastapi import APIRouter, Depends
from ..auth.auth import auth_handler
from src.routers.divgp import digp_router

router = APIRouter(
    dependencies=[Depends(auth_handler.decode_token)]
)
router.include_router(digp_router)

__all__ = ["router"]
