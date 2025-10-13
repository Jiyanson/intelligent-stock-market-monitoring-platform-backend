# app/db/base.py
from app.db.base_class import Base
from app.db.models.user import User
from app.db.models.watchlist import Watchlist

# Import all models here so Alembic can detect them
__all__ = ["Base", "User", "Watchlist"]