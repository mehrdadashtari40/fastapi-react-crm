# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import crud
from .api import auth, users, products

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Interview Backend")

# Allow your Next.js frontend (update with your Render URL later)
origins = [
    "http://localhost:3000",
    "https://your-nextjs-app.onrender.com"  # ← Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)

@app.on_event("startup")
def startup_event():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        crud.create_default_roles(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "FastAPI on Render.com with secure auth"}