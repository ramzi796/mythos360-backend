from sqlalchemy import Column, String, Integer, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "Users"

    userid = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    middlename = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String)
    role = Column(String)
    team = Column(String)
    department = Column(String)
    designation = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
