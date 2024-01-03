from pydantic import BaseModel
from datetime import datetime

# Create Venta Schema (Pydantic Model)
class VentaCreate(BaseModel):
    distribucion_id: int
    cantidad: float
    precio: float
    fecha: datetime
    punto_id: int
    pago_electronico: bool
    no_operacion: str | None
    pago_diferido: bool
    descripcion: str | None
    
# Complete Venta Schema (Pydantic Model)
class Venta(BaseModel):
    id: int
    distribucion_id: int
    cantidad: float
    precio: float
    monto: float
    fecha: datetime
    punto_id: int
    pago_electronico: bool
    no_operacion: str | None
    pago_diferido: bool
    descripcion: str | None
    usuario_id: int


class VentaGet(BaseModel):
    distribucion_id: int
    cantidad: float
    precio: float
    fecha: datetime
    punto_id: int
    nombre_producto: str
    pago_electronico: bool
    no_operacion: str | None
    pago_diferido: bool
    descripcion: str | None