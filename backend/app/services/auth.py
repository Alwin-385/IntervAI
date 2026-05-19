"""Authentication and Clerk user synchronization."""

import secrets

from app.core.auth.clerk import ClerkTokenPayload
from app.core.exceptions import UnauthorizedError, ValidationAppError
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user import UserRepository
from app.utils.security import hash_password


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def sync_user_from_clerk(self, payload: ClerkTokenPayload) -> User:
        if not payload.email:
            raise UnauthorizedError("Clerk token must include an email address")

        user = await self.user_repository.get_by_clerk_id(payload.clerk_user_id)
        if user:
            updates: dict = {}
            if user.email != payload.email:
                updates["email"] = payload.email
            if payload.full_name and user.full_name != payload.full_name:
                updates["full_name"] = payload.full_name
            if payload.image_url and user.avatar_url != payload.image_url:
                updates["avatar_url"] = payload.image_url
            if updates:
                user = await self.user_repository.update(user, updates)
            return user

        existing_email = await self.user_repository.get_by_email(payload.email)
        if existing_email:
            if existing_email.clerk_id and existing_email.clerk_id != payload.clerk_user_id:
                raise ValidationAppError(
                    "Email is already associated with another account",
                )
            return await self.user_repository.update(
                existing_email,
                {
                    "clerk_id": payload.clerk_user_id,
                    "full_name": payload.full_name or existing_email.full_name,
                    "avatar_url": payload.image_url,
                },
            )

        return await self.user_repository.create(
            {
                "clerk_id": payload.clerk_user_id,
                "email": payload.email,
                "full_name": payload.full_name or payload.email.split("@")[0],
                "hashed_password": hash_password(secrets.token_urlsafe(32)),
                "role": UserRole.CANDIDATE,
                "is_active": True,
                "avatar_url": payload.image_url,
            }
        )
