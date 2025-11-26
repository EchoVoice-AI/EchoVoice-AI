"""FastAPI router for uploading files to Azure Blob Storage.

This module provides an APIRouter with a POST /api/upload endpoint that
accepts an uploaded file and delegates to the storage helper to upload the
file as a blob, returning the blob URL and blob name on success.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from .. import storage

router = APIRouter()


@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> Any:
    """Upload a file to Azure Blob Storage and return the blob URL.

    The endpoint reads the uploaded file into memory and delegates to
    `storage.upload_blob`. For large files you should switch to a
    streaming approach or pre-signed upload.
    """
    try:
        # Stream upload: pass the internal file-like object to the storage
        # helper to avoid buffering large files into memory.
        blob_name = file.filename or "upload"
        url = storage.upload_fileobj_stream(file.file, blob_name, content_type=file.content_type)
        return {"url": url, "blob_name": blob_name}
    except RuntimeError as exc:
        # likely missing azure package or config
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")
