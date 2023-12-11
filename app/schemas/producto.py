from pydantic import BaseModel

# Create Producto Schema (Pydantic Model)
class ProductoCreate(BaseModel):
    nombre: str
    negocio_id: int|str
    
# Complete Producto Schema (Pydantic Model)
class Producto(BaseModel):
    id: int
    nombre: str
    negocio_id: int|str

    class Config:
        orm_mode = True