from pydantic import BaseModel

# Create Kiosko Schema (Pydantic Model)
class KioskoCreate(BaseModel):
    nombre: str
    representante: str
    activo: bool
    admin_id: int
    
# Complete Kiosko Schema (Pydantic Model)
class Kiosko(BaseModel):
    id: int
    nombre: str
    representante: str
    activo: bool
    admin_id: int

    class Config:
        orm_mode = True