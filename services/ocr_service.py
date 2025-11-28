import google.generativeai as genai
from PIL import Image
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


class OCRService:
    """OCR service using Google Gemini Vision API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro-latest"):
        """
        Initialize OCR service
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"OCR Service initialized with model: {model_name}")
    
    def extract_bill_data(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract structured bill data from image using Gemini Vision
        
        Args:
            image: PIL Image object of the bill
            
        Returns:
            Dictionary containing extracted bill data
        """
        try:
            # Create detailed prompt for bill extraction
            prompt = """
You are an expert at extracting data from bills and invoices. Analyze this bill/invoice image carefully and extract ALL line items with their details.

CRITICAL INSTRUCTIONS:
1. Extract EVERY line item - do not miss any entries.
2. Do not double-count any items.
3. For each line item, extract:
   - item_name: The product/service name or description
   - item_quantity: The quantity. If NOT present, use 0.0 (not null)
   - item_rate: The rate/price per unit. If NOT present, use 0.0 (not null)
   - item_amount: The total amount for that line item (REQUIRED - extract EXACTLY as shown, no rounding)

4. IMPORTANT: Only extract MONETARY values for item_amount. DO NOT extract:
   - Invoice dates or times
   - Invoice numbers or IDs
   - Patient IDs or registration numbers
   - Any non-currency values
   
5. Identify the page_type. It must be EXACTLY one of: "Bill Detail", "Final Bill", "Pharmacy"

6. Look for the "Total" or "Net Amount" printed on the bill.

7. Verify your work: Sum up the item_amount of all line items. Compare with the printed total.
   - If they don't match, check if you missed an item or included a sub-total by mistake.
   - Do NOT include "Sub Total" or "Tax" lines as separate line items if they are already part of the final total.

Return the data in this EXACT JSON format:
{
  "page_no": "1",
  "page_type": "Bill Detail",
  "line_items": [
    {
      "item_name": "Product Name",
      "item_quantity": 2.0,
      "item_rate": 100.50,
      "item_amount": 201.00
    }
  ],
  "extracted_total": 201.00,
  "actual_bill_total": 201.00
}

IMPORTANT RULES:
- Return ONLY valid JSON, no markdown formatting or code blocks.
- If item_rate is not present, set item_rate = 0.0
- If item_quantity is not present, set item_quantity = 0.0
- Item amount must be EXACTLY as shown in the document. No rounding allowed.
- page_type must be exactly one of: "Bill Detail", "Final Bill", "Pharmacy"
- Only extract currency amounts for item_amount (ignore dates, IDs, etc.)
"""
            
            logger.info("Sending image to Gemini Vision API for extraction")
            
            # Generate content with image
            response = self.model.generate_content([prompt, image])
            
            # Extract text from response
            response_text = response.text.strip()
            logger.info(f"Received response from Gemini: {response_text[:200]}...")
            
            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)
                logger.info(f"Successfully parsed JSON response with {len(extracted_data.get('line_items', []))} items")
                return extracted_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                # Return empty structure if parsing fails
                return {
                    "page_no": "1",
                    "line_items": [],
                    "extracted_total": 0.0,
                    "actual_bill_total": 0.0,
                    "error": f"JSON parsing error: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Error during bill extraction: {e}")
            return {
                "page_no": "1",
                "line_items": [],
                "extracted_total": 0.0,
                "actual_bill_total": 0.0,
                "error": str(e)
            }
