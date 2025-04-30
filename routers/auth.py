from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import user as models
from schemas import user as schemas
from utils import hash, jwt_handler

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash.hash_password(user.password)
    db_user = models.User(
        firstname=user.firstname,
        middlename=user.middlename,
        lastname=user.lastname,
        email=user.email,
        password_hash=hashed_pwd,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"status_code": 200, "detail": "User registered successfully"}

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not hash.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt_handler.create_access_token({"sub": db_user.email, "role": db_user.role})
    return {"status_code": 200, "access_token": token, "role": db_user.role, "detail": "User logged in successfully"}
