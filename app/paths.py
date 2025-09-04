from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = (BASE_DIR / 'uploads').resolve()

for d in (BASE_DIR, UPLOAD_DIR):
    d.mkdir(parents=True, exist_ok=True)