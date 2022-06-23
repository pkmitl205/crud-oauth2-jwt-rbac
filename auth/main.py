from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# pip install python-jose[cryptography]
from jose import JWTError, jwt

from . import crud, models, schemas
from .database import SessionLocal, engine
from .configs import TOKEN_EXPIRED_DAYS, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     user_token = crud.get_user_by_token(db,token)
#     if not user_token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     # check token expiration
#     now = datetime.now()
#     token_expired_date = user_token.created + timedelta(days=TOKEN_EXPIRED_DAYS)
#     if now <= token_expired_date:
#         return user_token
#     # remove expired token
#     crud.remove_token_by_user_name(user_token.user_name)
#     raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    invalid_credential = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},)
    try:
        print(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        #print(username)
        if username is None:
            raise invalid_credential
        user_token = crud.get_user_by_username(db,username)
        if not user_token:
            raise invalid_credential
    except JWTError:
        raise invalid_credential
    return user_token
    


def create_access_jwt_token(user_name: str):
    access_token_expires = timedelta(days=TOKEN_EXPIRED_DAYS)
    data_dict = {"username": user_name}
    to_encode = data_dict.copy()
    expire = datetime.utcnow() + access_token_expires    
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, user: schemas.UserToken = Depends(get_current_user),db: Session = Depends(get_db)):
        user_roles = crud.get_roles_by_username(db, user.user_name)
        roles = crud.get_role_names(db, user_roles)
        for role in roles:
            if role not in self.allowed_roles:
                raise HTTPException(status_code=403, detail="Operation not permitted")


############### HTTP Basic AUth ############### 
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

securityHttpBasic = HTTPBasic()

def challenge_http_basic_auth(credentials: HTTPBasicCredentials = Depends(securityHttpBasic),
        db: Session = Depends(get_db)):
    user_login= crud.authenticate_user(db,credentials.username,credentials.password)
    if not user_login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/users/basicauth")
def read_current_user(username: str = Depends(challenge_http_basic_auth)):
    return {"username": username}

##############################################   



@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_db = crud.get_user_by_username(db,user.user_name)
    if user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username was already taken",
        )
    return crud.create_user(db=db, user=user)

@app.post("/roles/", response_model=schemas.RoleRead)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    return crud.create_role(db=db, role=role)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/roles/", response_model=List[schemas.RoleRead])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = crud.get_roles(db, skip=skip, limit=limit)
    return roles

@app.get("/user/{user_id}/roles/", response_model=List[schemas.UserRole])
def read_roles_by_user_id(user_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles_by_user_id(db, user_id=user_id)
    return roles    

@app.post("/users/role", response_model=schemas.UserRole)
def insert_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    db_userrole = crud.insert_role_to_user(db, user_id=user_id, role_id=role_id)
    if db_userrole is None:
        raise HTTPException(status_code=404, detail="Failed to insert role to user")
    return db_userrole


# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user_login= crud.authenticate_user(db,form_data.username,form_data.password)
#     if not user_login:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user_token = crud.create_user_token(db,form_data.username)

#     return {"access_token": user_token.token, "token_type": "bearer"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_login= crud.authenticate_user(db,form_data.username,form_data.password)
    if not user_login:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_jwt_token = create_access_jwt_token(form_data.username)

    return {"access_token": user_jwt_token, "token_type": "bearer"}


# @app.get("/revoke")
# async def show_profile(user: schemas.UserToken = Depends(get_current_user),
#                 db: Session = Depends(get_db)):
#     crud.remove_token_by_user_name(db,user.user_name)
#     return {"message": "Your account was logout"}

@app.get("/users/myprofile", response_model=schemas.UserRead)
async def show_profile(user: schemas.UserToken = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return crud.get_user_by_username(db,user.user_name)



@app.get("/api/admin", dependencies=[Depends(RoleChecker(["ROLE_ADMIN"]))])
async def show_admin():
    return {"message":"this only for admin access"} 

@app.get("/api/manager", dependencies=[Depends(RoleChecker(["ROLE_MANAGER"]))])
async def show_manager():
    return {"message":"this only for manager access"} 

@app.get("/api/user", dependencies=[Depends(RoleChecker(["ROLE_USER"]))])
async def show_user():
    return {"message":"this only for user access"}       

@app.get("/api/manageruser", dependencies=[Depends(RoleChecker(["ROLE_USER","ROLE_MANAGER"]))])
async def show_manageruser():
    return {"message":"this only for user and manager accesses"}            