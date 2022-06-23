from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base

class Todo(Base):
    __tablename__ = "todos"
	
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String)
    is_completed = Column(Boolean, default=False)
    created = Column(DateTime, default=func.now())

