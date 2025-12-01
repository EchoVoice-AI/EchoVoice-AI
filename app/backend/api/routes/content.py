"""Content serving endpoints (files from blob storage)."""
import mimetypes
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from config import CONFIG_GLOBAL_BLOB_MANAGER, CONFIG_USER_BLOB_MANAGER, CONFIG_USER_UPLOAD_ENABLED
from ..dependencies import require_path_auth

router = APIRouter()


async def _require_path_dep(request: Request, path: str):
    return await require_path_auth(path, request)


@router.get("/content/{path:path}",tags=["Content"])
async def content_file(request: Request, path: str, auth_claims: dict = Depends(_require_path_dep)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    if "#page=" in path:
        path = path.split("#page=", 1)[0]

    global_blob: object = cfg.get(CONFIG_GLOBAL_BLOB_MANAGER)
    if not global_blob:
        raise HTTPException(status_code=503, detail="Global blob manager not configured")

    result = await global_blob.download_blob(path)

    if result is None and cfg.get(CONFIG_USER_UPLOAD_ENABLED):
        user_oid = auth_claims.get("oid")
        user_blob_manager = cfg.get(CONFIG_USER_BLOB_MANAGER)
        if user_blob_manager and user_oid:
            result = await user_blob_manager.download_blob(path, user_oid=user_oid)

    if not result:
        raise HTTPException(status_code=404, detail="File not found")

    content, properties = result
    if not properties or "content_settings" not in properties:
        raise HTTPException(status_code=404, detail="File metadata missing")

    mime_type = properties["content_settings"].get("content_type")
    if mime_type == "application/octet-stream":
        mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"

    return Response(content, media_type=mime_type)
