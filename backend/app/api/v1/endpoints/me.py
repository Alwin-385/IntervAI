"""Current user profile endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import MeResponse

router = APIRouter(tags=["auth"])


@router.get("/me", response_model=MeResponse)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeResponse:
    """Return the authenticated user synced from Clerk."""
    if not current_user.clerk_id:
        from app.core.exceptions import UnauthorizedError

        raise UnauthorizedError("Authenticated user is missing clerk_id")
    return MeResponse(
        id=current_user.id,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        clerk_id=current_user.clerk_id,
        avatar_url=current_user.avatar_url,
        clerk_user_id=current_user.clerk_id,
    )
