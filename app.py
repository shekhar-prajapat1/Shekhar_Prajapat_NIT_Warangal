from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from models import ExtractRequest, ExtractResponse, ExtractData
from config import config, Config
from services.document_processor import DocumentProcessor
from services.ocr_service import OCRService
from services.extraction_service import ExtractionService
from services.reconciliation_service import ReconciliationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    Config.validate()
    ocr_service = OCRService(api_key=config.GEMINI_API_KEY, model_name=config.GEMINI_MODEL)
    logger.info("Services initialized successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    ocr_service = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": config.API_TITLE,
        "version": config.API_VERSION
    }

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.post("/extract-bill-data", response_model=ExtractResponse)
async def extract_bill_data(request: ExtractRequest):
    """
    Extract line item details from bill/invoice images
    
    Args:
        request: ExtractRequest containing document URL
        
    Returns:
        ExtractResponse with extracted data or error
    """
    try:
        logger.info(f"Received extraction request for document: {request.document}")
        
        # Validate OCR service is initialized
        if ocr_service is None:
            raise HTTPException(
                status_code=500,
                detail="OCR service not initialized. Please check GEMINI_API_KEY configuration."
            )
        
        # Step 1: Download all pages
        images = DocumentProcessor.download_all_pages(str(request.document))
        if not images:
            return ExtractResponse(
                is_success=False,
                error="Failed to download document from provided URL"
            )
        
        logger.info(f"Processing {len(images)} page(s)")
        
        # Step 2 & 3: Process each page
        all_pagewise_items = []
        
        for page_num, image in enumerate(images, start=1):
            # Preprocess image
            image = DocumentProcessor.preprocess_image(image, config.MAX_IMAGE_SIZE)
            
            # Extract data using OCR
            ocr_data = ocr_service.extract_bill_data(image)
            
            # Check for OCR errors
            if "error" in ocr_data and not ocr_data.get("line_items"):
                logger.warning(f"OCR extraction failed for page {page_num}: {ocr_data['error']}")
                continue
            
            # Transform to structured line items
            pagewise_items = ExtractionService.transform_to_line_items(ocr_data)
            
            if pagewise_items and pagewise_items[0].bill_items:
                # Update page number
                pagewise_items[0].page_no = str(page_num)
                all_pagewise_items.extend(pagewise_items)
        
        if not all_pagewise_items:
            return ExtractResponse(
                is_success=False,
                error="No line items could be extracted from the document"
            )
        
        # Step 4: Calculate reconciled amount across all pages
        reconciled_amount = ReconciliationService.calculate_total(all_pagewise_items)
        total_item_count = ReconciliationService.count_items(all_pagewise_items)
        
        # Step 5: Prepare response
        extract_data = ExtractData(
            pagewise_line_items=all_pagewise_items,
            total_item_count=total_item_count,
            reconciled_amount=reconciled_amount
        )
        
        logger.info(
            f"Extraction successful: {len(images)} page(s), {total_item_count} items, "
            f"total amount: {reconciled_amount}"
        )
        
        return ExtractResponse(
            is_success=True,
            data=extract_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {e}", exc_info=True)
        return ExtractResponse(
            is_success=False,
            error=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
