"""User upload endpoints."""
import io
from fastapi import APIRouter, Depends, HTTPException, File, Request, UploadFile
from fastapi.responses import JSONResponse

from config import CONFIG_INGESTER, CONFIG_USER_BLOB_MANAGER, CONFIG_USER_UPLOAD_ENABLED
from prepdocslib.listfilestrategy import File as PrepFile
from ..dependencies import get_auth_claims

router = APIRouter()


@router.post("/upload",tags=["Uploads"])
async def upload(request: Request, file: UploadFile = File(...), auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    if not cfg.get(CONFIG_USER_UPLOAD_ENABLED):
        raise HTTPException(status_code=403, detail="User uploads are not enabled")

    user_oid = auth_claims.get("oid")
    if not user_oid:
        raise HTTPException(status_code=403, detail="Missing user identity")

    adls_manager = cfg.get(CONFIG_USER_BLOB_MANAGER)
    ingester = cfg.get(CONFIG_INGESTER)
    if adls_manager is None or ingester is None:
        raise HTTPException(status_code=503, detail="Upload backend not configured")

    try:
        content = await file.read()
        file_io = io.BytesIO(content)
        setattr(file_io, "name", file.filename)

        file_url = await adls_manager.upload_blob(file_io, file.filename, user_oid)

        prep_file = PrepFile(content=io.BytesIO(content), acls={"oids": [user_oid]}, url=file_url)
        await ingester.add_file(prep_file, user_oid=user_oid)

        return JSONResponse({"message": "File uploaded successfully"})
    except Exception as error:
        return JSONResponse({"message": "Error uploading file, check server logs for details.", "error": str(error)}, status_code=500)


@router.post("/delete_uploaded",tags=["Uploads"])
async def delete_uploaded(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    request_json = await request.json()
    filename = request_json.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    user_oid = auth_claims.get("oid")
    if not user_oid:
        raise HTTPException(status_code=403, detail="Missing user identity")

    adls_manager = cfg.get(CONFIG_USER_BLOB_MANAGER)
    ingester = cfg.get(CONFIG_INGESTER)
    if adls_manager is None:
        raise HTTPException(status_code=503, detail="User blob manager not configured")

    await adls_manager.remove_blob(filename, user_oid)
    if ingester:
        await ingester.remove_file(filename, user_oid)

    return JSONResponse({"message": f"File {filename} deleted successfully"})


@router.get("/list_uploaded",tags=["Uploads"])
async def list_uploaded(request: Request, auth_claims: dict = Depends(get_auth_claims)):
    cfg = getattr(request.app.state, "config", None)
    if cfg is None:
        raise HTTPException(status_code=503, detail="App not initialized")

    user_oid = auth_claims.get("oid")
    if not user_oid:
        raise HTTPException(status_code=403, detail="Missing user identity")

    adls_manager = cfg.get(CONFIG_USER_BLOB_MANAGER)
    if adls_manager is None:
        raise HTTPException(status_code=503, detail="User blob manager not configured")

    files = await adls_manager.list_blobs(user_oid)
    return JSONResponse(files)
