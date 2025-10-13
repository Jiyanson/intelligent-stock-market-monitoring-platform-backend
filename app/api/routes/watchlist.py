# app/api/routes/watchlist.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
import uuid

from app.db.session import get_async_session
from app.db.models.watchlist import Watchlist
from app.db.models.user import User
from app.schemas.watchlist import (
    WatchlistCreate, 
    WatchlistUpdate, 
    WatchlistResponse,
    WatchlistWithQuote
)
from app.core.fastapi_users import current_active_user
from app.services.finance_api import FinanceAPIService, FinanceAPIError

router = APIRouter()

@router.post("/", response_model=WatchlistResponse, status_code=201)
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Add a stock to user's watchlist"""
    
    # Validate symbol and get company info
    symbol = watchlist_data.symbol.upper().strip()
    
    try:
        # Verify the symbol exists by fetching quote
        quote_data = FinanceAPIService.get_stock_quote(symbol)
        
        # If company_name not provided, try to get it from company info
        company_name = watchlist_data.company_name
        if not company_name:
            try:
                company_info = FinanceAPIService.get_company_info(symbol)
                company_name = company_info.get('name')
            except:
                # If we can't get company info, just use the symbol
                company_name = symbol
                
    except FinanceAPIError as e:
        raise HTTPException(status_code=400, detail=f"Invalid stock symbol: {str(e)}")
    
    # Check if already in watchlist
    stmt = select(Watchlist).where(
        Watchlist.user_id == user.id,
        Watchlist.symbol == symbol
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=409, 
            detail=f"Stock {symbol} is already in your watchlist"
        )
    
    # Create watchlist item
    watchlist_item = Watchlist(
        user_id=user.id,
        symbol=symbol,
        company_name=company_name,
        notes=watchlist_data.notes
    )
    
    session.add(watchlist_item)
    await session.commit()
    await session.refresh(watchlist_item)
    
    return watchlist_item

@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlist(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get user's watchlist"""
    
    stmt = select(Watchlist).where(Watchlist.user_id == user.id).order_by(Watchlist.added_at.desc())
    result = await session.execute(stmt)
    watchlist_items = result.scalars().all()
    
    return watchlist_items

@router.get("/with-quotes", response_model=List[WatchlistWithQuote])
async def get_watchlist_with_quotes(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get user's watchlist with current stock quotes"""
    
    stmt = select(Watchlist).where(Watchlist.user_id == user.id).order_by(Watchlist.added_at.desc())
    result = await session.execute(stmt)
    watchlist_items = result.scalars().all()
    
    # Enrich with current quotes
    enriched_items = []
    for item in watchlist_items:
        item_dict = {
            "id": item.id,
            "user_id": item.user_id,
            "symbol": item.symbol,
            "company_name": item.company_name,
            "added_at": item.added_at,
            "notes": item.notes
        }
        
        # Try to get current quote
        try:
            quote_data = FinanceAPIService.get_stock_quote(item.symbol)
            item_dict.update({
                "current_price": quote_data.get('current_price'),
                "change": quote_data.get('change'),
                "change_percent": quote_data.get('change_percent'),
                "last_updated": quote_data.get('last_updated')
            })
        except:
            # If quote fetch fails, just return without quote data
            pass
        
        enriched_items.append(WatchlistWithQuote(**item_dict))
    
    return enriched_items

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist_item(
    watchlist_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific watchlist item"""
    
    stmt = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    )
    result = await session.execute(stmt)
    watchlist_item = result.scalar_one_or_none()
    
    if not watchlist_item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    return watchlist_item

@router.patch("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist_item(
    watchlist_id: uuid.UUID,
    update_data: WatchlistUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update a watchlist item (notes or company name)"""
    
    stmt = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    )
    result = await session.execute(stmt)
    watchlist_item = result.scalar_one_or_none()
    
    if not watchlist_item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(watchlist_item, field, value)
    
    await session.commit()
    await session.refresh(watchlist_item)
    
    return watchlist_item

@router.delete("/{watchlist_id}", status_code=204)
async def remove_from_watchlist(
    watchlist_id: uuid.UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Remove a stock from watchlist"""
    
    stmt = select(Watchlist).where(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == user.id
    )
    result = await session.execute(stmt)
    watchlist_item = result.scalar_one_or_none()
    
    if not watchlist_item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    await session.delete(watchlist_item)
    await session.commit()
    
    return None

@router.delete("/symbol/{symbol}", status_code=204)
async def remove_by_symbol(
    symbol: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Remove a stock from watchlist by symbol"""
    
    symbol = symbol.upper().strip()
    
    stmt = delete(Watchlist).where(
        Watchlist.user_id == user.id,
        Watchlist.symbol == symbol
    )
    result = await session.execute(stmt)
    await session.commit()
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404, 
            detail=f"Stock {symbol} not found in your watchlist"
        )
    
    return None

@router.get("/check/{symbol}")
async def check_in_watchlist(
    symbol: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Check if a symbol is in user's watchlist"""
    
    symbol = symbol.upper().strip()
    
    stmt = select(Watchlist).where(
        Watchlist.user_id == user.id,
        Watchlist.symbol == symbol
    )
    result = await session.execute(stmt)
    watchlist_item = result.scalar_one_or_none()
    
    return {
        "symbol": symbol,
        "in_watchlist": watchlist_item is not None,
        "watchlist_id": str(watchlist_item.id) if watchlist_item else None
    }