from pydantic import BaseModel

# Create Kiosko Schema (Pydantic Model)
class KioskoCreate(BaseModel):
    nombre: str
    representante: str
    activo: bool
    useradmin: str
    passwadmin: str
    
# Complete Kiosko Schema (Pydantic Model)
class Kiosko(BaseModel):
    id: int
    nombre: str
    representante: str
    activo: bool
    useradmin: str
    passwadmin: str