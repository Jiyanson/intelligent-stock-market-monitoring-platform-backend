from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import FastAPIUsers
from fastapi_users.authentication.jwt import JWTAuthentication
from fastapi_users.db.sqlalchemy import SQLAlchemyUserDatabase
from .db.session import SessionLocal
from .db.models import User
from .schemas import UserCreate, UserUpdate
from .users import fastapi_users, get_user_db

app = FastAPI()

# Dependency to get a database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Define the current_user dependency
def get_current_user(db: SQLAlchemyUserDatabase = Depends(get_user_db), token: str = Depends(JWTAuthentication(fastapi_users.auth_backends[0]))):
    return fastapi_users.current_user(token, db)

# Include FastAPI-Users router
app.include_router(
    fastapi_users.get_auth_router(JWTAuthentication),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(User, UserCreate, UserUpdate),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(User, UserUpdate),
    prefix="/users",
    tags=["users"]
)

@app.get("/users/me", response_model=User)
async def read_users_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return current_user

@app.on_event("startup")
async def startup_event():
    # Create tables if they do not exist
    async with SessionLocal() as session:
        await Base.metadata.create_all(bind=session.bind)

@app.on_event("shutdown")
async def shutdown_event():
    # No need to manually close the database connection
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)