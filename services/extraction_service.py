from typing import Dict, Any, List
from models import LineItem, PagewiseLineItems
import logging

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service to transform OCR output into structured line items"""
    
    @staticmethod
    def transform_to_line_items(ocr_data: Dict[str, Any]) -> List[PagewiseLineItems]:
        """
        Transform OCR extracted data into structured line items
        
        Args:
            ocr_data: Raw data from OCR service
            
        Returns:
            List of PagewiseLineItems
        """
        try:
            page_no = ocr_data.get("page_no", "1")
            page_type = ocr_data.get("page_type", "Bill Detail")
            raw_items = ocr_data.get("line_items", [])
            
            # Convert to LineItem objects
            line_items = []
            for item in raw_items:
                try:
                    line_item = LineItem(
                        item_name=item.get("item_name", "Unknown"),
                        item_amount=float(item.get("item_amount", 0.0)),
                        item_rate=float(item.get("item_rate", 0.0)),
                        item_quantity=float(item.get("item_quantity", 0.0))
                    )
                    line_items.append(line_item)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid line item: {item}. Error: {e}")
                    continue
            
            # Create pagewise structure
            pagewise_items = PagewiseLineItems(
                page_no=str(page_no),
                page_type=page_type,
                bill_items=line_items
            )
            
            logger.info(f"Transformed {len(line_items)} line items for page {page_no} (type: {page_type})")
            return [pagewise_items]
            
        except Exception as e:
            logger.error(f"Error transforming line items: {e}")
            return []
