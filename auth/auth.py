import schemas.token
import schemas.user
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import engine
import models.models as models
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "ce32120a340062fe6e11e77cf10cabcd05a76a381075e610ae66c69065bfd84b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1440)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(usuario, password):
   
    session = Session(bind=engine, expire_on_commit=False)
    user = session.query(models.User).where(models.User.usuario == usuario, models.User.activo == 1).first()

    if not user:
        return False

    if not pwd_context.verify(password, user.password):
        return False

    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pueden validar sus credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.token.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    session = Session(bind=engine, expire_on_commit=False)
    user = session.query(models.User).where(models.User.usuario == username, models.User.activo == 1).first()
    if user is None:
        raise credentials_exception
    return user



async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    if not current_user.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return current_user