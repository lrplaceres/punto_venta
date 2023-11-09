from pydantic import BaseModel

class User(BaseModel):
    usuario: str
    nombre: str | None = None
    email: str | None = None
    rol: str
    activo: bool | None = None


class UserInDB(User):
    password: str