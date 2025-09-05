import cv2
import numpy as np
from PIL import Image

from app.core import model

def has_text(img: Image.Image,
             conf_threshold: float = 0.5,
             width: int = 320,
             height: int = 320) -> bool:
    if model.net is None:
        raise RuntimeError("❌ EAST модель не загружена!")

    image = np.array(img)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    blob = cv2.dnn.blobFromImage(
        image, 1.0, (width, height),
        (123.68, 116.78, 103.94), True, False
    )
    model.net.setInput(blob)

    layer_names = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"
    ]
    scores, geometry = model.net.forward(layer_names)

    num_rows, num_cols = scores.shape[2:4]
    rects, confidences = [], []

    for y in range(num_rows):
        scores_data = scores[0, 0, y]
        x0_data = geometry[0, 0, y]
        x1_data = geometry[0, 1, y]
        x2_data = geometry[0, 2, y]
        x3_data = geometry[0, 3, y]
        angles_data = geometry[0, 4, y]

        for x in range(num_cols):
            score = scores_data[x]
            if score < conf_threshold:
                continue

            offset_x, offset_y = x * 4.0, y * 4.0
            angle = angles_data[x]
            cos, sin = np.cos(angle), np.sin(angle)

            h = x0_data[x] + x2_data[x]
            w = x1_data[x] + x3_data[x]

            end_x = int(offset_x + cos * x1_data[x] + sin * x2_data[x])
            end_y = int(offset_y - sin * x2_data[x] + cos * x3_data[x])
            start_x = int(end_x - w)
            start_y = int(end_y - h)

            rects.append((start_x, start_y, end_x, end_y))
            confidences.append(float(score))

    # Non-max suppression
    indices = cv2.dnn.NMSBoxes(
        [(*r[:2], r[2] - r[0], r[3] - r[1]) for r in rects],
        confidences,
        conf_threshold,
        0.4
    )

    # 👇 число регионов можно подстроить (3 → меньше ложняков)
    return len(indices) > 3
