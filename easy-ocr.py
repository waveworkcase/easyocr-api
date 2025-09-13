from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import easyocr
import shutil
import uvicorn
import base64
import numpy as np
import cv2
import os
import json
from datetime import datetime

app = FastAPI()
reader = easyocr.Reader(['th', 'en'])  # OCR ไทย + อังกฤษ

# ===== CONFIG =====
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
TEXT_DIR = "texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

JSON_FILE = os.path.join(TEXT_DIR, "ocr_result.json")  # ✅ เขียนทับไฟล์เดิมทุกครั้ง
MIN_CONFIDENCE = 0.1


def process_ocr(img, debug_filename=None):
    result = reader.readtext(
        img,
        detail=1,
        paragraph=False,
        contrast_ths=0.05,
        adjust_contrast=0.7,
        text_threshold=0.4,
        low_text=0.2
    )

    filtered_result = [res for res in result if res[2] >= MIN_CONFIDENCE]
    text_output = "\n".join([res[1] for res in filtered_result])

    print("=== OCR Result ===")
    ocr_json = []
    for (_, text, conf) in filtered_result:
        print(f"Text: {text} | Confidence: {conf:.2f}")
        ocr_json.append(text)

    # ✅ เขียนทับไฟล์ JSON เดิมเสมอ
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(ocr_json, f, ensure_ascii=False, indent=2)

    # debug image
    if debug_filename:
        debug_img = img.copy()
        for (bbox, text, conf) in filtered_result:
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(debug_img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(debug_img, text, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.imwrite(debug_filename, debug_img)

    return text_output, JSON_FILE


# 📌 Upload แบบไฟล์
@app.post("/ocr_file")
async def ocr_file(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.filename}")
    debug_path = os.path.join(OUTPUT_DIR, f"{timestamp}_debug.png")

    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    img = cv2.imread(original_path)
    text_output, json_path = process_ocr(img, debug_filename=debug_path)

    return JSONResponse(
        content={
            "text": text_output,
            "json_file": json_path
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


# 📌 Upload แบบ Base64
class OCRRequest(BaseModel):
    image_base64: str

@app.post("/ocr")
async def ocr_base64(req: OCRRequest):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_path = os.path.join(UPLOAD_DIR, f"{timestamp}_base64.png")
    debug_path = os.path.join(OUTPUT_DIR, f"{timestamp}_debug.png")

    image_data = base64.b64decode(req.image_base64)
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    cv2.imwrite(original_path, img)

    text_output, json_path = process_ocr(img, debug_filename=debug_path)

    return JSONResponse(
        content={
            "text": text_output,
            "json_file": json_path
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
