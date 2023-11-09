from fastapi import FastAPI, Depends
from routers import kiosko, producto, inventario, venta, user

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(kiosko.router)
app.include_router(producto.router)
app.include_router(inventario.router)
app.include_router(venta.router)
app.include_router(user.router)

@app.get("/")
def index(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"mensaje": "Bienvenido"}