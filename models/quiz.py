from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, BigInteger
from sqlalchemy.orm import relationship, Mapped
from .base import Base
from datetime import datetime



class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)

    
class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    question = Column(String)
    
    test = relationship('Test', lazy='selectin',foreign_keys=[test_id])
    answer = relationship('Answer', lazy='selectin')
    
class Answer(Base):
    __tablename__ = 'answers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    is_correct = Column(Boolean)
    answer = Column(String)

    question = relationship(Question,lazy='selectin', foreign_keys={question_id})
    
    
class UserTestAnswer(Base):
    __tablename__ = 'user_answers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    question_id = Column(Integer, ForeignKey('questions.id'))
    answer_id = Column(Integer, ForeignKey('answers.id'))
    time = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    question = relationship(Question,lazy='selectin', foreign_keys={question_id})
    answer = relationship(Answer, lazy='selectin', foreign_keys={answer_id})
    
class UserCompletedTest(Base):
    __tablename__ = 'user_completed'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    test_id = Column(Integer, ForeignKey('tests.id'))
    username = Column(String, nullable=True)
    
    test = relationship(Test,lazy='selectin' , foreign_keys={test_id})
    

    