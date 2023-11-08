from pydantic import BaseModel

# Create Producto Schema (Pydantic Model)
class ProductoCreate(BaseModel):
    nombre: str
    kiosko_id: int
    
# Complete Producto Schema (Pydantic Model)
class Producto(BaseModel):
    id: int
    nombre: str
    kiosko_id: int