# app/db/base.py
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from app.db.base_class import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    # optional extra columns
    first_name = Column(String, nullable=True)