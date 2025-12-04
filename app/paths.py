from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = (BASE_DIR / 'uploads').resolve()
STATIC_DIR = BASE_DIR / "app" / "static"

SMART_TMP_DIR = STATIC_DIR / "tmp_smart"
SMART_TMP_DIR.mkdir(parents=True, exist_ok=True)
print(SMART_TMP_DIR)

for d in (BASE_DIR, UPLOAD_DIR):
    d.mkdir(parents=True, exist_ok=True)