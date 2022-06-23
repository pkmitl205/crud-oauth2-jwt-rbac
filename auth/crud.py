from typing import List
from sqlalchemy.orm import Session, session
from sqlalchemy.sql.expression import false, true
from . import models, schemas
import bcrypt
import secrets

def create_user(db: Session, user: schemas.UserCreate):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode(),salt)
    db_user = models.User(user_name=user.user_name, 
                    full_name=user.full_name,
                    hashed_password=hashed_password,
                    salt=salt)
    db.add(db_user)	
    db.commit()
    db.refresh(db_user)
    return db_user

def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.Role(role_name=role.role_name)
    db.add(db_role)	
    db.commit()
    db.refresh(db_role)
    return db_role

def insert_role_to_user(db: Session, role_id: int, user_id: int):
    db_userrole = models.UserRole(role_id=role_id,user_id=user_id)
    db.add(db_userrole)	
    db.commit()
    db.refresh(db_userrole)
    return db_userrole

def remove_role_to_user(db: Session, role_id: int, user_id: int):
    db_userrole = models.UserRole(role_id=role_id,user_id=user_id)
    db.delete(db_userrole)
    db.commit()
    db.refresh(db_userrole)
    return db_userrole

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_roles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Role).offset(skip).limit(limit).all()

def get_roles_by_user_id(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.user_roles

def get_roles_by_username(db: Session, username: str):
    user = db.query(models.User).filter(models.User.user_name == username).first()
    return user.user_roles

def get_role_names(db: Session, roles: List[models.UserRole]):
    names = list()
    for role in roles:
        role_item = db.query(models.Role).filter(models.Role.id == role.id).first()
        names.append(role_item.role_name)

    return names   

def get_user_by_username(db: Session, username: str):
    user = db.query(models.User).filter(models.User.user_name == username).first()
    return user

def authenticate_user(db: Session, username: str, password: str):
    user_login = db.query(models.User).filter(models.User.user_name == username).first()
    if user_login:
        salt = user_login.salt
        hashed_password = bcrypt.hashpw(password.encode(),salt)
        if user_login.hashed_password == hashed_password:
           return user_login
   
    return None

def create_user_token(db: Session, user_name: str):
    user_token = secrets.token_hex(30)
    db_user_token = db.query(models.UserToken).filter(models.UserToken.user_name == user_name).first()
    if db_user_token:    
        db_user_token.token = user_token
    else:
        db_user_token = models.UserToken(user_name=user_name, 
                        token=user_token)
    db.add(db_user_token)	
    db.commit()
    db.refresh(db_user_token)
    return db_user_token

def get_user_by_token(db: Session, token: str):
    user_token = db.query(models.UserToken).filter(models.UserToken.token == token).first()
    return user_token

def remove_token_by_user_name(db: Session, user_name: str):
    user_token = db.query(models.UserToken).filter(models.UserToken.user_name == user_name).first()
    db.delete(user_token)
    db.commit()
    return user_token
