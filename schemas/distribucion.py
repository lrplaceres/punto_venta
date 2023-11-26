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