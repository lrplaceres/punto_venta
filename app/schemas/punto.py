from pydantic import BaseModel

# Create Punto Schema (Pydantic Model)
class PuntoCreate(BaseModel):
    nombre: str
    direccion: str
    negocio_id: int|str
    
# Complete Punto (Pydantic Model)
class Punto(BaseModel):
    id: int
    nombre: str
    direccion: str
    negocio_id: int|str

    class Config:
        orm_mode = True