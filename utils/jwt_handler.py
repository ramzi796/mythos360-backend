from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mythos360")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
