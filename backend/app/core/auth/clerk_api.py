"""Clerk Backend API helpers when JWT claims are incomplete."""

from __future__ import annotations

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)

CLERK_API_BASE = "https://api.clerk.com/v1"


async def fetch_clerk_user_profile(
    clerk_user_id: str,
    secret_key: str,
) -> tuple[str | None, str | None, str | None]:
    """
    Fetch email and profile from Clerk when the session JWT omits them.

    Returns (email, full_name, image_url).
    """
    url = f"{CLERK_API_BASE}/users/{clerk_user_id}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {secret_key}"},
        )
        if response.status_code == 404:
            logger.warning("clerk_user_not_found", clerk_user_id=clerk_user_id)
            return None, None, None
        response.raise_for_status()
        data = response.json()

    email: str | None = None
    addresses = data.get("email_addresses") or []
    primary_id = data.get("primary_email_address_id")
    for entry in addresses:
        if not isinstance(entry, dict):
            continue
        if primary_id and entry.get("id") == primary_id:
            email = entry.get("email_address")
            break
    if not email and addresses:
        first = addresses[0]
        if isinstance(first, dict):
            email = first.get("email_address")

    first_name = data.get("first_name") or ""
    last_name = data.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip() or None
    image_url = data.get("image_url") or data.get("profile_image_url")

    return email, full_name, image_url
