"""User business logic."""

from uuid import UUID

from app.core.exceptions import ConflictError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse, PaginationQuery
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.base import BaseService
from app.utils.security import hash_password


class UserService(BaseService[UserRepository, UserResponse]):
    def __init__(self, repository: UserRepository) -> None:
        super().__init__(repository)

    @staticmethod
    def _to_response(user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def create_user(self, payload: UserCreate) -> UserResponse:
        existing = await self.repository.get_by_email(payload.email)
        if existing:
            raise ConflictError(f"User with email '{payload.email}' already exists")
        user = await self.repository.create(
            {
                "email": payload.email,
                "hashed_password": hash_password(payload.password),
                "full_name": payload.full_name,
                "role": payload.role,
                "is_active": True,
            }
        )
        return self._to_response(user)

    async def get_user(self, user_id: UUID) -> UserResponse:
        user = await self.repository.get_by_id_or_raise(user_id, resource="User")
        return self._to_response(user)

    async def list_users(
        self,
        pagination: PaginationQuery,
        *,
        active_only: bool = True,
    ) -> PaginatedResponse[UserResponse]:
        page, page_size = self.pagination_params(pagination)
        result = await self.repository.list_active(
            page=page,
            page_size=page_size,
            active_only=active_only,
        )
        return self.to_paginated_response(result, self._to_response)

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> UserResponse:
        user = await self.repository.get_by_id_or_raise(user_id, resource="User")
        data = payload.model_dump(exclude_unset=True)
        if "email" in data and data["email"] != user.email:
            existing = await self.repository.get_by_email(data["email"])
            if existing:
                raise ConflictError(f"User with email '{data['email']}' already exists")
        if "password" in data:
            data["hashed_password"] = hash_password(data.pop("password"))
        updated = await self.repository.update(user, data)
        return self._to_response(updated)

    async def delete_user(self, user_id: UUID) -> None:
        user = await self.repository.get_by_id_or_raise(user_id, resource="User")
        await self.repository.delete(user)
