"""FastAPI authentication dependencies."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.auth.clerk import ClerkTokenPayload, enrich_payload_from_clerk_api, verify_clerk_token
from app.core.dependencies import get_user_repository
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService

_bearer = HTTPBearer(auto_error=False)


async def get_token_payload(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ],
) -> ClerkTokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing Bearer authentication token")
    payload = verify_clerk_token(credentials.credentials)
    settings = get_settings()
    return await enrich_payload_from_clerk_api(payload, settings.clerk_secret_key)


async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(user_repo)


async def get_current_user(
    payload: Annotated[ClerkTokenPayload, Depends(get_token_payload)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    return await auth_service.sync_user_from_clerk(payload)


async def get_optional_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer),
    ],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    try:
        payload = verify_clerk_token(credentials.credentials)
        settings = get_settings()
        payload = await enrich_payload_from_clerk_api(payload, settings.clerk_secret_key)
        return await auth_service.sync_user_from_clerk(payload)
    except UnauthorizedError:
        return None
