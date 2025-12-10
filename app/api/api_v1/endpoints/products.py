# app/api/api_v1/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.api_v1.deps import get_db_safe  # Solo importamos get_db_safe
# Quitamos: get_current_active_user, get_current_superuser
from app.schemas.product import ProductCreate, ProductOut
from app.crud.crud_product import get_products, create_product, get_product, get_product_by_sku, update_product, delete_product

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductOut)
def create_new_product(product_in: ProductCreate, db: Session = Depends(get_db_safe)):
    """Crear nuevo producto (ahora es público)"""
    existing = get_product_by_sku(db, product_in.sku)
    if existing:
        raise HTTPException(400, "Producto con ese SKU ya existe")
    return create_product(db, product_in)


@router.get("/", response_model=List[ProductOut])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_safe)):
    """Listar productos (ahora es público)"""
    return get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductOut)
def get_product_by_id(product_id: int, db: Session = Depends(get_db_safe)):
    """Obtener producto por ID (ahora es público)"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product_endpoint(product_id: int, product_in: ProductCreate, db: Session = Depends(get_db_safe)):
    """Actualizar producto (ahora es público)"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    data = product_in.dict()
    return update_product(db, product, data)


@router.delete("/{product_id}")
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db_safe)):
    """Eliminar producto (ahora es público)"""
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    delete_product(db, product)
    return {"detail": "Producto eliminado"}