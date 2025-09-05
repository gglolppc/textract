from app.paths import BASE_DIR
import cv2

EAST_MODEL = BASE_DIR / "weights" / "frozen_east_text_detection.pb"
net = None