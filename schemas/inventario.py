from pydantic import BaseModel
from datetime import date

# Create inventario Schema (Pydantic Model)
class InventarioCreate(BaseModel):
    producto_id: int
    cantidad: float
    um: str
    costo: float
    fecha: date
    kiosko_id: int
    
# Complete Inventario Schema (Pydantic Model)
class Inventario(BaseModel):
    id: int
    producto_id: int
    cantidad: float
    um: str
    costo: float
    fecha: date
    kiosko_id: int

    class Config:
        orm_mode = True