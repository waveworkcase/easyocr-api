# EasyOCR API

เซอร์วิส OCR ที่ใช้ FastAPI สำหรับแยกข้อความจากรูปภาพด้วย EasyOCR รองรับภาษาไทยและอังกฤษ

## คุณสมบัติ

- แยกข้อความจากรูปภาพ รองรับภาษาไทยและอังกฤษ
- รับข้อมูลได้ 2 วิธี: อัปโหลดไฟล์และ base64 encoded images
- แสดงผลลัพธ์แบบ debug พร้อมกรอบข้อความ
- ส่งออกผลลัพธ์เป็น JSON
- กรองผลลัพธ์ตามค่าความเชื่อมั่น
- ปรับแต่งและประมวลผลรูปภาพอัตโนมัติ

## การติดตั้ง

1. โคลนโปรเจค:
```bash
git clone <repository-url>
cd easyocr-api
```

2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

## การใช้งาน

### เริ่มเซอร์เวอร์
```bash
python easy-ocr.py
```

API จะใช้งานได้ที่ `http://localhost:8000`

### API Endpoints

#### 1. อัปโหลดไฟล์ - `/ocr_file` (POST)

อัปโหลดไฟล์รูปภาพเพื่อประมวลผล OCR

**คำขอ:**
- Method: POST
- Content-Type: multipart/form-data
- Body: ไฟล์รูปภาพ

**ตัวอย่าง:**
```bash
curl -X POST "http://localhost:8000/ocr_file" \
  -F "file=@your-image.jpg"
```

#### 2. รูปภาพ Base64 - `/ocr` (POST)

ส่งรูปภาพแบบ base64 encoded เพื่อประมวลผล OCR

**คำขอ:**
- Method: POST
- Content-Type: application/json
- Body:
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

**ตัวอย่าง:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "your-base64-encoded-image"}'
```

### รูปแบบการตอบกลับ

ทั้งสอง endpoint จะคืนค่า:

```json
{
  "text": "ข้อความที่แยกได้จากรูปภาพ",
  "json_file": "path/to/ocr_result.json"
}
```

## การตั้งค่า

การตั้งค่าสำคัญในโค้ด:

- **ภาษา**: ไทย (`th`) และอังกฤษ (`en`)
- **ค่าความเชื่อมั่นขั้นต่ำ**: 0.1 (ปรับได้ผ่าน `MIN_CONFIDENCE`)
- **โฟลเดอร์อัปโหลด**: `uploads/`
- **โฟลเดอร์ผลลัพธ์**: `outputs/` (รูปภาพ debug)
- **โฟลเดอร์ข้อความ**: `texts/` (ผลลัพธ์ JSON)

## ไฟล์ผลลัพธ์

เซอร์วิสจะสร้างโฟลเดอร์และไฟล์:

- `uploads/` - เก็บรูปภาพที่อัปโหลดพร้อม timestamp
- `outputs/` - รูปภาพ debug ที่แสดงขอบเขตข้อความ
- `texts/ocr_result.json` - ผลลัพธ์ OCR ล่าสุดในรูปแบบ JSON

## Dependencies

- FastAPI - Web framework
- EasyOCR - ไลบรารี OCR
- OpenCV - ประมวลผลรูปภาพ
- Pydantic - ตรวจสอบข้อมูล
- Uvicorn - ASGI server

## เอกสาร API

เมื่อเซอร์เวอร์ทำงาน เข้าชมได้ที่:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`