# from sqlalchemy import Column, Integer, String, VARCHAR
# from database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer,primary_key=True,autoincrement=True)
#     name = Column(String(50))
#     age = Column(Integer)
#     gender = Column(String(20))
#     address = Column(String(50))
#     phone = Column(String(10),unique=True)
    

# class Admin(Base):
#     __tablename__ = "admin"

#     id = Column(Integer,primary_key=True,autoincrement=True)
#     fullname = Column(String(50))
#     username = Column(String(50),unique=True)
#     password = Column(VARCHAR(50),unique=True)
#     reconfirm_password = Column(VARCHAR(50),unique=True)


from sqlalchemy import Column, Integer, String
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
