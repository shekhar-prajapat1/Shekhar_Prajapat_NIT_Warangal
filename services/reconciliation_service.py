from typing import List
from models import PagewiseLineItems
import logging

logger = logging.getLogger(__name__)


class ReconciliationService:
    """Service to reconcile extracted amounts and validate totals"""
    
    @staticmethod
    def calculate_total(pagewise_items: List[PagewiseLineItems]) -> float:
        """
        Calculate total amount from all line items without double-counting
        
        Args:
            pagewise_items: List of pagewise line items
            
        Returns:
            Total reconciled amount
        """
        total = 0.0
        
        for page in pagewise_items:
            for item in page.bill_items:
                total += item.item_amount
        
        # Round to 2 decimal places to avoid floating point errors
        total = round(total, 2)
        
        logger.info(f"Calculated total: {total}")
        return total
    
    @staticmethod
    def count_items(pagewise_items: List[PagewiseLineItems]) -> int:
        """
        Count total number of line items
        
        Args:
            pagewise_items: List of pagewise line items
            
        Returns:
            Total item count
        """
        count = sum(len(page.bill_items) for page in pagewise_items)
        logger.info(f"Total item count: {count}")
        return count
    
    @staticmethod
    def validate_extraction(reconciled_amount: float, actual_bill_total: float, tolerance: float = 0.01) -> bool:
        """
        Validate if extracted amount matches actual bill total within tolerance
        
        Args:
            reconciled_amount: Amount calculated from extracted line items
            actual_bill_total: Actual total from the bill
            tolerance: Acceptable difference percentage (default 1%)
            
        Returns:
            True if amounts match within tolerance
        """
        if actual_bill_total == 0:
            return reconciled_amount == 0
        
        difference = abs(reconciled_amount - actual_bill_total)
        percentage_diff = (difference / actual_bill_total) * 100
        
        is_valid = percentage_diff <= tolerance
        
        logger.info(
            f"Validation: Reconciled={reconciled_amount}, "
            f"Actual={actual_bill_total}, "
            f"Difference={difference} ({percentage_diff:.2f}%), "
            f"Valid={is_valid}"
        )
        
        return is_valid
