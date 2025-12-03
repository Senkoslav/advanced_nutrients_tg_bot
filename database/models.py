from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(BigInteger, unique=True, index=True)
    
    username = Column(String, nullable=True)
    early_access = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

class QuestionMapping(Base):
    """Таблица для связи сообщений админа с пользователями"""
    __tablename__ = 'question_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_message_id = Column(BigInteger, unique=True, index=True)  
    user_id = Column(BigInteger)  
    created_at = Column(DateTime, default=datetime.utcnow)