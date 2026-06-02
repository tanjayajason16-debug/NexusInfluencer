import io
import mimetypes
import os
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


class StorageError(Exception):
    pass


def get_storage_backend():
    return current_app.config.get("STORAGE_BACKEND", "local").lower()


def save_file(upload, media_type):
    backend = get_storage_backend()
    if backend == "s3":
        return save_file_s3(upload, media_type)
    return save_file_local(upload, media_type)


def delete_file(file_path):
    backend = get_storage_backend()
    if backend == "s3":
        delete_file_s3(file_path)
    else:
        delete_file_local(file_path)


def open_file(file_path):
    backend = get_storage_backend()
    if backend == "s3":
        return download_file_s3(file_path)
    return open_file_local(file_path)


def local_storage_root():
    return Path(current_app.config["UPLOAD_FOLDER"])


def save_file_local(upload, media_type):
    upload_root = local_storage_root()
    target_dir = upload_root / media_type
    target_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(upload.filename)
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    filename = f"{uuid4().hex}.{extension}" if extension else uuid4().hex
    destination = target_dir / filename
    upload.save(destination)

    return str(Path("uploads") / media_type / filename).replace("\\", "/")


def open_file_local(file_path):
    relative_path = Path(file_path)
    if relative_path.parts and relative_path.parts[0] == "uploads":
        relative_path = Path(*relative_path.parts[1:])
    path = local_storage_root() / relative_path
    if not path.exists() or not path.is_file():
        raise StorageError("Local file not found.")
    return path


def delete_file_local(file_path):
    try:
        path = open_file_local(file_path)
    except StorageError:
        return
    if path.exists() and path.is_file():
        path.unlink()


def download_file_s3(file_path):
    client = _create_s3_client()
    bucket = _s3_bucket_name()

    try:
        response = client.get_object(Bucket=bucket, Key=file_path)
        body = response["Body"].read()
    except Exception as exc:
        raise StorageError(f"S3 download failed: {exc}") from exc

    buffer = io.BytesIO(body)
    content_type = response.get("ContentType") or mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    buffer.seek(0)
    return buffer, content_type


def delete_file_s3(file_path):
    client = _create_s3_client()
    bucket = _s3_bucket_name()
    try:
        client.delete_object(Bucket=bucket, Key=file_path)
    except Exception as exc:
        raise StorageError(f"S3 delete failed: {exc}") from exc


def save_file_s3(upload, media_type):
    client = _create_s3_client()
    bucket = _s3_bucket_name()
    original_name = secure_filename(upload.filename)
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    key = f"{media_type}/{uuid4().hex}.{extension}" if extension else f"{media_type}/{uuid4().hex}"

    try:
        data = upload.read()
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=upload.mimetype or "application/octet-stream",
        )
    except Exception as exc:
        raise StorageError(f"S3 upload failed: {exc}") from exc

    return key


def _create_s3_client():
    try:
        import boto3
    except ImportError as exc:
        raise StorageError("boto3 is required for S3 storage backend. Install it in your environment.") from exc

    kwargs = {}
    region = current_app.config.get("S3_REGION")
    endpoint_url = current_app.config.get("S3_ENDPOINT_URL")
    access_key = current_app.config.get("S3_ACCESS_KEY_ID")
    secret_key = current_app.config.get("S3_SECRET_ACCESS_KEY")

    if region:
        kwargs["region_name"] = region
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    if access_key and secret_key:
        kwargs["aws_access_key_id"] = access_key
        kwargs["aws_secret_access_key"] = secret_key

    return boto3.client("s3", **kwargs)


def _s3_bucket_name():
    bucket = current_app.config.get("S3_BUCKET_NAME")
    if not bucket:
        raise StorageError("S3_BUCKET_NAME must be configured for the S3 storage backend.")
    return bucket
