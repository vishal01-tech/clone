from sqlalchemy import Column, Integer, String , VARCHAR , DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20))
    address = Column(String(50))


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=True)
    phone = Column(String(15), unique=True, nullable=True)
    otp = Column(VARCHAR(6))  
    otp_expiry = Column(DateTime, nullable=True)
