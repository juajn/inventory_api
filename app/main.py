# app/main.py
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.api_v1.endpoints import auth, users, products, inventory
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Inventory API")

# CORS (ajusta orígenes en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# crea tablas si no existen (útil en dev)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Inventory API - FastAPI"}

# registrar routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
