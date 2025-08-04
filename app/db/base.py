from app.db.base_class import Base
from app.db.models.user import User

# Import all models here so Alembic can detect them
__all__ = ["Base", "User"]