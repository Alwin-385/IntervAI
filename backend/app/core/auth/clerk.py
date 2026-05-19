"""Clerk JWT verification via JWKS."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import jwt
from jwt import PyJWKClient, PyJWTError

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class ClerkTokenPayload:
    """Validated Clerk session token claims."""

    clerk_user_id: str
    email: str | None
    full_name: str | None
    image_url: str | None

    @classmethod
    def from_claims(cls, claims: dict) -> ClerkTokenPayload:
        clerk_user_id = claims.get("sub")
        if not clerk_user_id:
            raise UnauthorizedError("Token missing subject (sub) claim")

        email = _first_str(claims.get("email"))
        if not email and isinstance(claims.get("email_addresses"), list):
            for entry in claims["email_addresses"]:
                if isinstance(entry, dict) and entry.get("email_address"):
                    email = entry["email_address"]
                    break

        full_name = _first_str(claims.get("name"))
        if not full_name:
            first = _first_str(claims.get("given_name")) or ""
            last = _first_str(claims.get("family_name")) or ""
            combined = f"{first} {last}".strip()
            full_name = combined or None

        image_url = _first_str(claims.get("image_url")) or _first_str(claims.get("picture"))

        return cls(
            clerk_user_id=clerk_user_id,
            email=email,
            full_name=full_name,
            image_url=image_url,
        )


def _first_str(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


@lru_cache
def _get_jwk_client(issuer: str) -> PyJWKClient:
    jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def verify_clerk_token(token: str, settings: Settings | None = None) -> ClerkTokenPayload:
    """Verify a Clerk session JWT and return typed claims."""
    cfg = settings or get_settings()

    if not cfg.clerk_jwt_issuer:
        raise UnauthorizedError("Clerk JWT issuer is not configured on the server")

    try:
        signing_key = _get_jwk_client(cfg.clerk_jwt_issuer).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=cfg.clerk_jwt_issuer,
            options={
                "verify_aud": False,
                "require": ["sub", "iss", "exp"],
            },
        )
    except PyJWTError as exc:
        logger.warning("clerk_token_verification_failed", error=str(exc))
        raise UnauthorizedError("Invalid or expired authentication token") from exc

    return ClerkTokenPayload.from_claims(claims)
