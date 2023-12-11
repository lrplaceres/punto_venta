from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: str
    rol: str
    name: str


class TokenData(BaseModel):
    usuario: str | None = None