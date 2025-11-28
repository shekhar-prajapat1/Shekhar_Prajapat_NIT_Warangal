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
            prompt = """Extract all line items from this medical bill/invoice image.

For each line item, provide:
- item_name: product/service name
- item_quantity: quantity (use 0.0 if not shown)
- item_rate: price per unit (use 0.0 if not shown)  
- item_amount: total amount (REQUIRED - exact value, no rounding)

IMPORTANT:
- Only extract MONETARY amounts (not dates, invoice numbers, or IDs)
- page_type must be one of: "Bill Detail", "Final Bill", or "Pharmacy"
- Use 0.0 for missing quantity/rate values
- Extract amounts exactly as shown

Return ONLY this JSON (no markdown, no code blocks):
{
  "page_no": "1",
  "page_type": "Bill Detail",
  "line_items": [
    {
      "item_name": "Item 1",
      "item_quantity": 1.0,
      "item_rate": 100.0,
      "item_amount": 100.0
    }
  ],
  "extracted_total": 100.0,
  "actual_bill_total": 100.0
}
"""
            
            logger.info("Sending image to Gemini Vision API for extraction")
            
            # Generate content with image
            response = self.model.generate_content([prompt, image])
            
            # Extract text from response
            response_text = response.text.strip()
            logger.info(f"Received response from Gemini: {response_text[:200]}...")
            
            # Clean up response (remove markdown code blocks if present)
            if "```json" in response_text:
                # Extract content between ```json and ```
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end]
            elif response_text.startswith("```"):
                # Remove opening ```
                response_text = response_text[3:]
                # Remove closing ```
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
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                
                # Try to ask Gemini again with stricter JSON format
                repair_prompt = f"""The previous response had invalid JSON. Please fix it and return ONLY valid JSON with no special characters in strings.

Previous response:
{response_text[:1000]}

Return corrected JSON with properly escaped quotes."""
                
                try:
                    repair_response = self.model.generate_content(repair_prompt)
                    repaired_text = repair_response.text.strip()
                    
                    # Clean again
                    if "```json" in repaired_text:
                        start = repaired_text.find("```json") + 7
                        end = repaired_text.find("```", start)
                        if end != -1:
                            repaired_text = repaired_text[start:end]
                    
                    repaired_text = repaired_text.strip()
                    extracted_data = json.loads(repaired_text)
                    logger.info("Successfully repaired and parsed JSON")
                    return extracted_data
                except:
                    pass
                
                # Last resort: return empty structure
                return {
                    "page_no": "1",
                    "page_type": "Bill Detail",
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
