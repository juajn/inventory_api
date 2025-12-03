# app/schemas/inventory.py
from pydantic import BaseModel
from typing import Optional


class InventoryBase(BaseModel):
    product_id: int
    quantity: int


class InventoryUpdate(BaseModel):
    quantity: int


class InventoryOut(InventoryBase):
    id: int
    updated_at: Optional[str]

    class Config:
        orm_mode = True
