from fastapi import APIRouter, Body, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from auth.auth_utils import get_current_user
from schemas.user import UserCreate
from utils.hash import hash_password
import csv
import random
import string
from utils.email_service import send_login_email

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can access this")
    return db.query(User).all()

@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        firstname=user.firstname,
        email=user.email,
        role=user.role,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status_code": 200, "detail": "User created", "userid": new_user.userid}

@router.delete("/users/{userid}")
def delete_user(userid: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    user = db.query(User).filter(User.userid == userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"status_code": 200, "detail": "User deleted"}

@router.post("/users/bulk-upload")
def bulk_upload_users(
    file: UploadFile = File(...),
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload users in bulk")

    contents = file.file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(contents)

    created = 0
    skipped = 0
    summary = []

    for row in reader:
        email = row.get("email")
        firstname = row.get("firstname")
        role = row.get("role")
        password = row.get("password") or generate_random_password()

        if not email or not firstname or not role:
            skipped += 1
            continue

        if db.query(User).filter(User.email == email).first():
            skipped += 1
            continue

        new_user = User(
            firstname=firstname,
            email=email,
            role=role,
            password_hash=hash_password(password)
        )
        db.add(new_user)
        created += 1
        summary.append({"email": email, "password": password})
        if send_email:
            try:
                send_login_email(email, firstname, password)
            except Exception as e:
                print(f"Failed to email {email}: {e}")

    db.commit()
    return {
        "created": created,
        "skipped": skipped,
        "summary": summary if send_email or summary else None
    }

@router.patch("/users/{userid}/update")
def update_user_details(
    userid: int,
    update: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update user info")

    user = db.query(User).filter(User.userid == userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update allowed fields only
    for key in ["firstname", "middlename", "lastname", "role"]:
        if key in update:
            setattr(user, key, update[key])

    db.commit()
    db.refresh(user)
    return {
        "status_code": 200,
        "detail": "User updated", 
        "user": {
            "userid": user.userid, 
            "firstname": user.firstname, 
            "middlename": user.middlename,
            "lastname": user.lastname,
            "role": user.role
        }
    }

@router.patch("/users/{userid}/reset-password")
def reset_user_password(
    userid: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can reset passwords")

    user = db.query(User).filter(User.userid == userid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password = generate_random_password()
    user.password_hash = hash_password(new_password)

    db.commit()
    return {"status_code": 200, "detail": "Password reset", "new_password": new_password}