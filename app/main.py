from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.db.base import Base
from app.db.session import engine
from app.api.api_v1.endpoints import auth, users, products, inventory
import os

app = FastAPI(title="Inventory API")

# Configuración CORS MEJORADA
origins = [
    "http://localhost:5173",      # Vite dev server
    "http://localhost:3000",      # Create React App
    "http://127.0.0.1:5173",      # Localhost alternativo
    "https://tu-frontend.com",    # Tu dominio en producción
]

# Si estás en desarrollo, permite también el puerto actual
if os.getenv("ENVIRONMENT") == "development":
    origins.append("http://localhost:*")
    origins.append("http://127.0.0.1:*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Allow-Headers",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=600,  # 10 minutos para cache de preflight
)

# IMPORTANTE: Para depuración, agrega middleware personalizado
@app.middleware("http")
async def add_cors_debug_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Agregar headers CORS explícitos para debug
    origin = request.headers.get("origin")
    if origin and origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    # Debug en consola
    if request.method == "OPTIONS":
        print(f"🔧 Preflight request from: {origin}")
    
    return response

# crea tablas si no existen (útil en dev)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Inventory API - FastAPI"}

# Endpoint para probar CORS
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Manejador explícito para OPTIONS requests"""
    return JSONResponse(
        content={"message": "CORS preflight"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With",
            "Access-Control-Max-Age": "600",
        }
    )

# registrar routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")