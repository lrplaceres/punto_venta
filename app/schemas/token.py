from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    usuario: str
    rol: str
    name: str


class TokenData(BaseModel):
    usuario: str | None = None