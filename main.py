from fastapi import FastAPI, Depends, HTTPException, status
from routers import kiosko, producto, inventario, venta, user
import schemas.token as schemaToken
import schemas.user as schemaUser

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import auth.auth as auth
from datetime import datetime, timedelta
import models.models as models
from typing import Annotated

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(kiosko.router)
app.include_router(producto.router)
app.include_router(inventario.router)
app.include_router(venta.router)
app.include_router(user.router)


@app.post("/token", response_model=schemaToken.Token)
async def login_for_access_token(form_data: Annotated[auth.OAuth2PasswordRequestForm, Depends()]):

    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.usuario}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "usuario":user.usuario, "rol":user.rol, "name":user.nombre}


@app.get("/users/me/", response_model=schemaUser.User)
async def read_users_me(current_user: Annotated[models.User, Depends(auth.get_current_active_user)]):
    return current_user
