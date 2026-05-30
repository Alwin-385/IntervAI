"""Synchronous storage reads for Celery workers."""

from __future__ import annotations

from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings


def _resolve_local_base(cfg: Settings) -> Path:
    base = Path(cfg.storage_local_path)
    if not base.is_absolute():
        backend_root = Path(__file__).resolve().parents[2]
        base = (backend_root / base).resolve()
    return base


def read_storage_bytes(storage_key: str, settings: Settings | None = None) -> bytes:
    cfg = settings or get_settings()
    if cfg.storage_backend == "local":
        path = _resolve_local_base(cfg) / storage_key
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found at {path}")
        return path.read_bytes()

    if not cfg.s3_bucket:
        raise RuntimeError("S3 bucket is not configured")

    client = boto3.client(
        "s3",
        region_name=cfg.s3_region,
        endpoint_url=cfg.s3_endpoint_url,
        aws_access_key_id=cfg.s3_access_key_id,
        aws_secret_access_key=cfg.s3_secret_access_key,
    )
    try:
        response = client.get_object(Bucket=cfg.s3_bucket, Key=storage_key)
        return response["Body"].read()
    except ClientError as exc:
        raise FileNotFoundError(f"S3 object missing: {storage_key}") from exc
