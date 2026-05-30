"""Local filesystem storage backend."""

from pathlib import Path

import aiofiles

from app.storage.base import StorageBackend, StoredObject


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: Path) -> None:
        self._base = base_path.resolve()
        self._base.mkdir(parents=True, exist_ok=True)

    def _full_path(self, key: str) -> Path:
        path = (self._base / key).resolve()
        if not str(path).startswith(str(self._base)):
            raise ValueError("Invalid storage key path")
        return path

    async def save(self, key: str, data: bytes, content_type: str) -> StoredObject:
        path = self._full_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
        return StoredObject(
            key=key,
            uri=f"local://{key}",
            size_bytes=len(data),
        )

    async def delete(self, key: str) -> None:
        path = self._full_path(key)
        if path.exists():
            path.unlink()

    async def exists(self, key: str) -> bool:
        return self._full_path(key).exists()

    def public_uri(self, key: str) -> str:
        return f"local://{key}"
