from fastapi import FastAPI
from routers import kiosko, producto, mercancia, venta

app = FastAPI()

app.include_router(kiosko.router)
app.include_router(producto.router)
app.include_router(mercancia.router)
app.include_router(venta.router)

@app.get("/")
def index():
    return {"mensaje": "Bienvenido"}