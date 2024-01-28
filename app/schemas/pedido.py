from pydantic import BaseModel
from datetime import date, datetime
    
# Complete Negocioema (Pydantic Model)
class Pedido(BaseModel):
    cantidad: float
    distribucion_id: int
    id: int
    precio: float
    punto_id: int
    nombre_producto: str
    nombre_punto: str

    class Config:
        orm_mode = True

