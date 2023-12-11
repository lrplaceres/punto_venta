from pydantic import BaseModel
from datetime import date, datetime

# Create distribucion Schema (Pydantic Model)
class DistribucionCreate(BaseModel):
    inventario_id: int
    cantidad: float
    fecha: datetime   
    punto_id: int
    
# Complete distribucion Schema (Pydantic Model)
class Distribucion(BaseModel):
    id: int
    inventario_id: int
    cantidad: float
    fecha: datetime   
    punto_id: int

    class Config:
        orm_mode = True


class DistribucionGet(BaseModel):
    id: int
    cantidad: float
    fecha: datetime   
    inventario_id: int
    punto_id: int
    negocio_id: int
    cantidad_inventario: float
    cantidad_distribuida: float