"""S3-compatible object storage backend."""

import asyncio

import boto3
from botocore.exceptions import ClientError

from app.storage.base import StorageBackend, StoredObject


class S3StorageBackend(StorageBackend):
    def __init__(
        self,
        bucket: str,
        region: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self._bucket = bucket
        session = boto3.session.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self._client = session.client("s3", endpoint_url=endpoint_url)

    async def save(self, key: str, data: bytes, content_type: str) -> StoredObject:
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return StoredObject(
            key=key,
            uri=f"s3://{self._bucket}/{key}",
            size_bytes=len(data),
        )

    async def delete(self, key: str) -> None:
        try:
            await asyncio.to_thread(
                self._client.delete_object,
                Bucket=self._bucket,
                Key=key,
            )
        except ClientError:
            pass

    async def exists(self, key: str) -> bool:
        try:
            await asyncio.to_thread(
                self._client.head_object,
                Bucket=self._bucket,
                Key=key,
            )
            return True
        except ClientError:
            return False

    def public_uri(self, key: str) -> str:
        return f"s3://{self._bucket}/{key}"
