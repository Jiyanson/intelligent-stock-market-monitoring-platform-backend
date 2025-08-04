from fastapi import FastAPI, Depends
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.fastapi_users import fastapi_users, current_active_user
from app.core.auth import auth_backend
from app.db.models.user import User
from app.api.routes.ping import router as ping_router

app = FastAPI(
    title="Stock Market Monitoring Platform",
    description="A production-ready FastAPI backend with FastAPI Users authentication",
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

# Include other routes
app.include_router(ping_router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Stock Market Monitoring Platform API with FastAPI Users",
        "version": "1.0.0",
        "docs": "/docs",
        "auth_endpoints": {
            "register": "/auth/register",
            "login": "/auth/jwt/login",
            "logout": "/auth/jwt/logout",
            "users": "/users/me"
        }
    }

@app.get("/protected-route")
async def protected_route(user: User = Depends(current_active_user)):
    return {
        "message": f"Hello {user.email}! This is a protected route.",
        "user_id": str(user.id)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)