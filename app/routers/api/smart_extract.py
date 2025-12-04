from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_session
from app.routers.auth.dependencies import get_current_user_or_none
from app.services.smart_extract import (
    save_temp_file,
    process_files,
    export_excel,
    export_pdf,
    save_table_to_db,
)
from app.db.database import ExtractLog

router = APIRouter(prefix="/api/smart-extract", tags=["Smart Extract"])


# ------------------------------------------------------------
# Upload single file → save to temp → return file_id + preview
# ------------------------------------------------------------
@router.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user_or_none),
):
    file_id, preview_url = await save_temp_file(file, user)
    return {"file_id": file_id, "preview_url": preview_url}


# ------------------------------------------------------------
# Process all files → GPT → return JSON table
# ------------------------------------------------------------
@router.post("/process")
async def process_request(
    body: dict,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user_or_none),
):
    file_ids: list[str] = body.get("file_ids")
    mode: str = body.get("mode", "simple")

    if not file_ids:
        raise HTTPException(400, "No files supplied")

    table_json = await process_files(file_ids, mode, user)

    # Save JSON to DB
    log = await save_table_to_db(session, user, table_json)

    return {
        "log_id": log.id,
        "table": table_json,
    }


# ------------------------------------------------------------
# Export Excel
# ------------------------------------------------------------
@router.post("/export/excel")
async def export_excel_route(body: dict, user=Depends(get_current_user_or_none)):
    table = body.get("table")
    if not table:
        raise HTTPException(400, "Table missing")

    file_bytes = export_excel(table)
    return file_bytes


# ------------------------------------------------------------
# Export PDF
# ------------------------------------------------------------
@router.post("/export/pdf")
async def export_pdf_route(body: dict, user=Depends(get_current_user_or_none)):
    table = body.get("table")
    if not table:
        raise HTTPException(400, "Table missing")

    file_bytes = export_pdf(table)
    return file_bytes


# ------------------------------------------------------------
# Save to history
# ------------------------------------------------------------
@router.post("/save")
async def save_table(body: dict,
                     session: AsyncSession = Depends(get_session),
                     user=Depends(get_current_user_or_none)):
    table = body.get("table")
    if not table:
        raise HTTPException(400, "Table missing")

    log = await save_table_to_db(session, user, table)
    return {"status": "ok", "log_id": log.id}
