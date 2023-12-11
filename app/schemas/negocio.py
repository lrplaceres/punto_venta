from pydantic import BaseModel
from datetime import date, datetime

# Create Negocio Schema (Pydantic Model)
class NegocioCreate(BaseModel):
    nombre: str
    direccion: str
    informacion: str
    fecha_licencia: datetime
    activo: bool
    propietario_id: int
    
# Complete Negocioema (Pydantic Model)
class Negocio(BaseModel):
    id: int
    nombre: str
    direccion: str
    informacion: str
    fecha_licencia: datetime
    activo: bool
    propietario_id: int

    class Config:
        orm_mode = True