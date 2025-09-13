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
from datetime import datetime

app = FastAPI()
reader = easyocr.Reader(['th', 'en'])  # อ่านได้ทั้งไทย + อังกฤษ

# ===== CONFIG =====
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
TEXT_DIR = "texts"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

MIN_CONFIDENCE = 0.1   # ปรับค่าความมั่นใจขั้นต่ำ

# ===== Helper Function =====
def process_ocr(img, timestamp, debug_filename=None):
    result = reader.readtext(
        img,
        detail=1,
        paragraph=False,
        contrast_ths=0.05,
        adjust_contrast=0.7,
        text_threshold=0.4,
        low_text=0.2
    )

    # กรองตามความมั่นใจ
    filtered_result = [res for res in result if res[2] >= MIN_CONFIDENCE]

    # รวมข้อความ (ตามลำดับ OCR ส่งมา)
    text_output = "\n".join([res[1] for res in filtered_result])

    # ✅ แสดงใน Terminal (รองรับ UTF-8 ถ้าใช้ VSCode/PowerShell)
    print("=== OCR Result ===")
    for res in filtered_result:
        print(f"Text: {res[1]} | Confidence: {res[2]:.2f}")

    # เซฟข้อความลงไฟล์ UTF-8
    txt_path = os.path.join(TEXT_DIR, f"{timestamp}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text_output)

    # วาดกรอบ Debug แล้วเซฟ
    if debug_filename:
        debug_img = img.copy()
        for (bbox, text, conf) in filtered_result:
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(debug_img, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(debug_img, text, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.imwrite(debug_filename, debug_img)
        print(f"[INFO] Debug image saved at {debug_filename}")

    return text_output, txt_path

# 📌 กรณี 1: รับไฟล์ตรง (multipart/form-data)
@app.post("/ocr_file")
async def ocr_file(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{file.filename}")
    debug_path = os.path.join(OUTPUT_DIR, f"{timestamp}_debug.png")

    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    img = cv2.imread(original_path)
    text_output, txt_path = process_ocr(img, timestamp, debug_filename=debug_path)

    return JSONResponse(
        content={
            "text": text_output,
            "original_file": original_path,
            "debug_file": debug_path,
            "text_file": txt_path
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# 📌 กรณี 2: รับ base64 JSON
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

    text_output, txt_path = process_ocr(img, timestamp, debug_filename=debug_path)

    return JSONResponse(
        content={
            "text": text_output,
            "original_file": original_path,
            "debug_file": debug_path,
            "text_file": txt_path
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
