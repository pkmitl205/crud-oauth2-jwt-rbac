from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.sql.sqltypes import Boolean


class UserRole(BaseModel):
    id: int
    user_id: int
    role_id: int
    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):	
    pass

class RoleRead(RoleBase):
    id: int
    created: datetime	
    class Config:
        orm_mode = True

class Role(RoleBase):
    id: int
    created: datetime	
    users: List[UserRole] = []
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    user_name: str
    full_name: str

class UserCreate(UserBase):	
    password: str

class UserRead(UserBase):
    id: int
    created: datetime	
    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    created: datetime	
    roles: List[UserRole] = []
    class Config:
        orm_mode = True

class UserLogin(BaseModel):    
    user_name: str
    password: int

class UserToken(BaseModel):    
    user_name: str
    token: str