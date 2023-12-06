from pydantic import BaseModel

class User(BaseModel):
    usuario: str
    nombre: str | None = None
    email: str | None = None
    rol: str
    activo: bool | None = None

    class Config:
        orm_mode = True


class UserInDB(User):
    password: str


class UserList(User):
    id: int

class UserEdit(BaseModel):
    nombre: str | None = None
    email: str | None = None
    rol: str
    activo: bool | None = None

class UserCambiaPassword(BaseModel):
    contrasenna_nueva: str
    repite_contrasenna_nueva: str
    contrasenna_actual: str