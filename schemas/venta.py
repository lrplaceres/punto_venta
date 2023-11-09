from pydantic import BaseModel
from datetime import date

# Create Venta Schema (Pydantic Model)
class VentaCreate(BaseModel):
    mercancia_id: int
    cantidad: float
    precio: float
    fecha: date
    kiosko_id: int
    
# Complete Venta Schema (Pydantic Model)
class Venta(BaseModel):
    id: int
    mercancia_id: int
    cantidad: float
    precio: float
    fecha: date
    kiosko_id: int