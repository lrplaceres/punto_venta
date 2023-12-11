from pydantic import BaseModel

class Dependiente(BaseModel):
    usuario: str
    nombre: str | None = None
    email: str | None = None
    activo: bool | None = None
    punto_id: int | str

    class Config:
        orm_mode = True


class DependienteCreate(Dependiente):
    password: str


class  DependienteList(Dependiente):
    id: int


class DependienteEdit(BaseModel):
    nombre: str | None = None
    email: str | None = None
    activo: bool | None = None
    punto_id: int


class DependienteCambiaPasswordPropietario(BaseModel):
    contrasenna_nueva: str
    repite_contrasenna_nueva: str