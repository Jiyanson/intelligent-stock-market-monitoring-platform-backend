# app/schemas/watchlist.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

class WatchlistCreate(BaseModel):
    """Schema for creating a watchlist item"""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol (e.g., AAPL, MSFT)")
    company_name: Optional[str] = Field(None, max_length=255, description="Company name (optional)")
    notes: Optional[str] = Field(None, max_length=500, description="Personal notes about the stock")

class WatchlistUpdate(BaseModel):
    """Schema for updating a watchlist item"""
    notes: Optional[str] = Field(None, max_length=500, description="Update personal notes")
    company_name: Optional[str] = Field(None, max_length=255, description="Update company name")

class WatchlistResponse(BaseModel):
    """Schema for watchlist item response"""
    id: uuid.UUID
    user_id: uuid.UUID
    symbol: str
    company_name: Optional[str]
    added_at: datetime
    notes: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class WatchlistWithQuote(BaseModel):
    """Schema for watchlist item with current stock quote"""
    id: uuid.UUID
    user_id: uuid.UUID
    symbol: str
    company_name: Optional[str]
    added_at: datetime
    notes: Optional[str]
    current_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[str] = None
    last_updated: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)