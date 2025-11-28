from services.document_processor import DocumentProcessor
from services.ocr_service import OCRService
from config import config
import json

url = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A21%3A03Z&se=2026-11-25T14%3A21%3A00Z&sr=b&sp=r&sig=2szJobwLVzcVSmg5IPWjRT9k7pHq2Tvifd6seRa2xRI%3D"

print("Step 1: Download image...")
images = DocumentProcessor.download_all_pages(url)
print(f"Downloaded: {len(images)} image(s)")

if images:
    image = DocumentProcessor.preprocess_image(images[0])
    print(f"Image size: {image.size}, mode: {image.mode}")
    
    print("\nStep 2: OCR extraction...")
    ocr_service = OCRService(api_key=config.GEMINI_API_KEY, model_name=config.GEMINI_MODEL)
    result = ocr_service.extract_bill_data(image)
    
    print("\nOCR Result:")
    print(json.dumps(result, indent=2))
