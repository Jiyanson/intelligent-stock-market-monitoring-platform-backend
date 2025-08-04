import uuid
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String
from app.db.base_class import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    # Additional fields beyond the base user model
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)