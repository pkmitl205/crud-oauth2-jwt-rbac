from sqlalchemy import Boolean, ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"
	
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    full_name = Column(String)
    hashed_password = Column(String)
    salt = Column(String)
    created = Column(DateTime, default=func.now())

    user_roles = relationship("UserRole", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, index=True)
    created = Column(DateTime, default=func.now())

    user_roles = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "userroles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

class UserToken(Base):
    __tablename__ = "usertokens"
	
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    token = Column(String)
    created = Column(DateTime, default=func.now())
