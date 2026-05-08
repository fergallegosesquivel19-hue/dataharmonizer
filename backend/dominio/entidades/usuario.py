from pydantic import BaseModel, EmailStr
from typing import Optional

class Usuario(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    nombre: str
    password_hash: str
    es_admin: bool = False
