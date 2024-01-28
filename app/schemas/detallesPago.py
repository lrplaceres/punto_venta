from pydantic import BaseModel
from datetime import date, datetime
    
# Complete Negocioema (Pydantic Model)
class detallesPago(BaseModel):
    fecha: datetime
    pago_electronico: bool
    no_operacion: str
    punto_id: int

    class Config:
        orm_mode = True