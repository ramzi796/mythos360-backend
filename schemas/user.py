from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    firstname: str
    middlename: Optional[str]
    lastname: Optional[str]
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str
