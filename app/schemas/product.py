# app/schemas/product.py
from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    name: str
    sku: str
    price: float
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True
