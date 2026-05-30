"""Storage backend abstraction (local filesystem or S3-compatible)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class StoredObject:
    """Reference to a stored file."""

    key: str
    uri: str
    size_bytes: int


class StorageBackend(ABC):
    """Abstract storage for resume PDFs."""

    @abstractmethod
    async def save(self, key: str, data: bytes, content_type: str) -> StoredObject:
        """Persist bytes and return storage metadata."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove an object by key."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check whether an object exists."""

    @abstractmethod
    def public_uri(self, key: str) -> str:
        """Return a URI/path reference stored on the resume record."""
