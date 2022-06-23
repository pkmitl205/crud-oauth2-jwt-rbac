from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import Boolean

class TodoBase(BaseModel):
    task_name: str
    is_completed: bool

class TodoCreate(TodoBase):	
    pass

class TodoUpdate(TodoBase):
    id: int

class Todo(TodoBase):
    id: int
    created: datetime	
    class Config:
        orm_mode = True