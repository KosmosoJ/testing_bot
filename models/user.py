from sqlalchemy import Column, Integer, String, BigInteger
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)    
    tg_id = Column(BigInteger, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)

