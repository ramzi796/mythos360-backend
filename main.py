from fastapi import FastAPI
from routers import auth
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend port
    allow_credentials=True,
    allow_methods=["*"],                      # <-- Must allow OPTIONS
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
