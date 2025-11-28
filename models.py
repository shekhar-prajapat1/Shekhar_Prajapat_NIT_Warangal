from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional


class ExtractRequest(BaseModel):
    """Request model for bill extraction"""
    document: HttpUrl = Field(..., description="URL to the bill/invoice image")


class LineItem(BaseModel):
    """Individual line item from a bill"""
    item_name: str = Field(..., description="Name/description of the item")
    item_amount: float = Field(..., description="Total amount for this line item")
    item_rate: float = Field(0.0, description="Rate/price per unit (0.0 if not present)")
    item_quantity: float = Field(0.0, description="Quantity of items (0.0 if not present)")


class PagewiseLineItems(BaseModel):
    """Line items grouped by page number"""
    page_no: str = Field(..., description="Page number")
    page_type: str = Field(..., description="Type of page: Bill Detail, Final Bill, or Pharmacy")
    bill_items: List[LineItem] = Field(..., description="List of line items on this page")


class ExtractData(BaseModel):
    """Extracted data from the bill"""
    pagewise_line_items: List[PagewiseLineItems] = Field(
        ..., description="Line items organized by page"
    )
    total_item_count: int = Field(..., description="Total number of line items")
    reconciled_amount: float = Field(
        ..., description="Total amount reconciled from all line items"
    )


class ExtractResponse(BaseModel):
    """Response model for bill extraction"""
    is_success: bool = Field(..., description="Whether extraction was successful")
    data: Optional[ExtractData] = Field(None, description="Extracted data if successful")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
