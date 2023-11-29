from pydantic import BaseModel
from datetime import date, datetime

# Create Venta Schema (Pydantic Model)
class VentaCreate(BaseModel):
    distribucion_id: int
    cantidad: float
    precio: float
    fecha: datetime
    punto_id: int
    usuario_id: int
    
# Complete Venta Schema (Pydantic Model)
class Venta(BaseModel):
    id: int
    distribucion_id: int
    cantidad: float
    precio: float
    fecha: datetime
    punto_id: int
    usuario_id: int