# app/schemas/inventory.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryBase(BaseModel):
    product_id: int = Field(..., gt=0, description="ID del producto")
    quantity: int = Field(..., ge=0, description="Cantidad en inventario")


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., description="Cantidad a ajustar (positiva para agregar, negativa para restar)")


class InventoryCreate(InventoryBase):
    """Esquema para crear inventario"""
    pass


class InventoryOut(InventoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class InventoryResponse(BaseModel):
    """Respuesta estándar para operaciones de inventario"""
    success: bool
    message: str
    data: Optional[InventoryOut] = None


class InventoryListResponse(BaseModel):
    """Respuesta para listar inventario"""
    success: bool
    count: int
    data: list[InventoryOut]


class InventoryAdjustResponse(BaseModel):
    """Respuesta específica para ajuste de inventario"""
    success: bool
    message: str
    previous_quantity: int
    new_quantity: int
    adjustment: int
    product_id: int