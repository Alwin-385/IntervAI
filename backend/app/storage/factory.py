"""Storage backend factory."""

from functools import lru_cache
from pathlib import Path

from app.core.config import Settings, get_settings
from app.storage.base import StorageBackend
from app.storage.local import LocalStorageBackend
from app.storage.s3 import S3StorageBackend


@lru_cache
def get_storage_backend(settings: Settings | None = None) -> StorageBackend:
    cfg = settings or get_settings()
    if cfg.storage_backend == "s3":
        if not cfg.s3_bucket:
            raise RuntimeError("S3_BUCKET is required when STORAGE_BACKEND=s3")
        return S3StorageBackend(
            bucket=cfg.s3_bucket,
            region=cfg.s3_region,
            endpoint_url=cfg.s3_endpoint_url,
            access_key=cfg.s3_access_key_id,
            secret_key=cfg.s3_secret_access_key,
        )
    base = Path(cfg.storage_local_path)
    if not base.is_absolute():
        # Resolve relative to backend/ so paths match sync extraction reads
        backend_root = Path(__file__).resolve().parents[2]
        base = (backend_root / base).resolve()
    return LocalStorageBackend(base)


@lru_cache
def get_audio_storage_backend(settings: Settings | None = None) -> StorageBackend:
    cfg = settings or get_settings()
    if cfg.storage_backend == "s3":
        if not cfg.s3_bucket:
            raise RuntimeError("S3_BUCKET is required when STORAGE_BACKEND=s3")
        return S3StorageBackend(
            bucket=cfg.s3_bucket,
            region=cfg.s3_region,
            endpoint_url=cfg.s3_endpoint_url,
            access_key=cfg.s3_access_key_id,
            secret_key=cfg.s3_secret_access_key,
        )
    base = Path(cfg.storage_audio_path)
    if not base.is_absolute():
        backend_root = Path(__file__).resolve().parents[2]
        base = (backend_root / base).resolve()
    return LocalStorageBackend(base)
