# app/main.py
from fastapi import FastAPI, Depends
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.fastapi_users import fastapi_users, current_active_user
from app.core.auth import auth_backend
from app.db.models.user import User
from app.api.routes.ping import router as ping_router
from app.api.routes.finance import router as finance_router

app = FastAPI(
    title="Stock Market Monitoring Platform",
    description="A production-ready FastAPI backend with FastAPI Users authentication and Alpha Vantage integration",
    version="1.0.0"
)

# Include authentication routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend), 
    prefix="/auth/jwt", 
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include API routes
app.include_router(ping_router, prefix="/api/v1", tags=["health"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Stock Market Monitoring Platform API with Alpha Vantage",
        "version": "1.0.0",
        "docs": "/docs",
        "auth_endpoints": {
            "register": "/auth/register",
            "login": "/auth/jwt/login",
            "logout": "/auth/jwt/logout",
            "users": "/users/me"
        },
        "finance_endpoints": {
            "search_stocks": "/api/v1/finance/search/stocks",  # NEW: Featured endpoint
            "quote": "/api/v1/finance/quote/{symbol}",
            "historical": "/api/v1/finance/historical/{symbol}",
            "search": "/api/v1/finance/search",
            "movers": "/api/v1/finance/movers",
            "company": "/api/v1/finance/company/{symbol}",
            "news": "/api/v1/finance/news",
            "market_status": "/api/v1/finance/market-status",
            "multiple_quotes": "/api/v1/finance/quotes/multiple",
            "health": "/api/v1/finance/health"
        },
        "examples": {
            "search_stocks": {
                "url": "/api/v1/finance/search/stocks?company_name=Apple&limit=5",
                "description": "Search for stocks by company name",
                "auth_required": True
            },
            "get_quote": {
                "url": "/api/v1/finance/quote/AAPL",
                "description": "Get current stock price",
                "auth_required": True
            }
        }
    }

@app.get("/protected-route")
async def protected_route(user: User = Depends(current_active_user)):
    return {
        "message": f"Hello {user.email}! This is a protected route.",
        "user_id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name
    }

# Startup event to ensure database is ready
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    # Import here to avoid circular imports
    from app.db.init_db import create_tables
    await create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)