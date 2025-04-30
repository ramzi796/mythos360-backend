from pydantic import BaseModel

class UserCreate(BaseModel):
    firstname: str
    middlename: str
    lastname: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str
