from fastapi import FastAPI
from routers import auth
from database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
