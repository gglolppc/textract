import uuid
import json
import shutil
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.paths import SMART_TMP_DIR      # создашь путь
from app.db.database import ExtractLog
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# ---------------------------------------------
# Save temp file
# ---------------------------------------------
async def save_temp_file(file: UploadFile, user):
    file_id = str(uuid.uuid4())
    user_folder = SMART_TMP_DIR / str(user.id if user else "guest")
    user_folder.mkdir(parents=True, exist_ok=True)

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(400, "Only JPG/PNG allowed")

    file_path = user_folder / f"{file_id}{file_ext}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    preview_url = f"/static/tmp_smart/{user.id}/{file_path.name}"

    return file_id, preview_url


# ---------------------------------------------
# Extract text from ONE image (GPT stub)
# ---------------------------------------------
async def extract_single_image(img_path, mode):
    """
    TODO: replace this stub with real GPT extraction
    Must return: [{"name": "...", "v1": ..., "v2": ..., "total": ...}, ...]
    """

    # Simulated extracted data
    return [
        {"name": "Item A", "v1": 10, "v2": 2, "total": 20},
        {"name": "Item B", "v1": 5, "v2": 4, "total": 20},
    ]


# ---------------------------------------------
# Process multiple files → unify JSON
# ---------------------------------------------
async def process_files(file_ids: list[str], mode: str, user):
    user_folder = SMART_TMP_DIR / str(user.id if user else "guest")

    final_rows = []

    for file_id in file_ids:
        # get real path
        matches = list(user_folder.glob(f"{file_id}.*"))
        if not matches:
            continue

        img_path = matches[0]

        # Extract with GPT
        extracted = await extract_single_image(img_path, mode)

        final_rows.extend(extracted)

        # cleanup file
        try:
            img_path.unlink()
        except:
            pass

    return final_rows


# ---------------------------------------------
# Save JSON to DB
# ---------------------------------------------
async def save_table_to_db(session: AsyncSession, user, table_json):
    log = ExtractLog(
        user_id=user.id if user else None,
        json_data=table_json,
        created_at=datetime.utcnow(),
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


# ---------------------------------------------
# Export Excel
# ---------------------------------------------
from openpyxl import Workbook
from fastapi.responses import StreamingResponse
from io import BytesIO

def export_excel(table):
    wb = Workbook()
    ws = wb.active

    # headers
    if table:
        ws.append(list(table[0].keys()))

    # rows
    for row in table:
        ws.append(list(row.values()))

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=table.xlsx"},
    )


# ---------------------------------------------
# Export PDF
# ---------------------------------------------
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def export_pdf(table):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    x, y = 40, 800

    # header
    if table:
        for h in table[0].keys():
            c.drawString(x, y, str(h))
            x += 120

        y -= 25
        x = 40

    # rows
    for row in table:
        for val in row.values():
            c.drawString(x, y, str(val))
            x += 120

        x = 40
        y -= 20

    c.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=table.pdf"},
    )
