from pydantic import BaseModel
from datetime import date

# Create Mercancia Schema (Pydantic Model)
class MercanciaCreate(BaseModel):
    producto_id: int
    cantidad: float
    um: str
    costo: float
    fecha: date
    kiosko_id: int
    
# Complete Mercancia Schema (Pydantic Model)
class Mercancia(BaseModel):
    id: int
    producto_id: int
    cantidad: float
    um: str
    costo: float
    fecha: date
    kiosko_id: int