# app/api/api_v1/endpoints/inventory.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.api_v1.deps import get_db_safe, get_current_active_user, get_current_superuser
from app.crud.crud_inventory import get_inventory_by_product, create_or_update_inventory, adjust_inventory
from app.crud.crud_product import get_product
from app.schemas.inventory import InventoryOut, InventoryBase, InventoryUpdate

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{product_id}", response_model=InventoryOut, dependencies=[Depends(get_current_active_user)])
def get_inventory(product_id: int, db: Session = Depends(get_db_safe)):
    inv = get_inventory_by_product(db, product_id)
    if not inv:
        raise HTTPException(404, "Inventario no encontrado")
    return inv


@router.post("/", response_model=InventoryOut, dependencies=[Depends(get_current_superuser)])
def create_or_update(inv_in: InventoryBase, db: Session = Depends(get_db_safe)):
    product = get_product(db, inv_in.product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return create_or_update_inventory(db, inv_in.product_id, inv_in.quantity)


@router.patch("/{product_id}", response_model=InventoryOut, dependencies=[Depends(get_current_superuser)])
def adjust(product_id: int, delta: InventoryUpdate, db: Session = Depends(get_db_safe)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return adjust_inventory(db, product_id, delta.quantity)
