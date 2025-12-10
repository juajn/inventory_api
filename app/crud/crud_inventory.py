# app/crud/crud_inventory.py
from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.models.product import Product
from typing import List, Optional


def get_inventory_by_product(db: Session, product_id: int) -> Optional[Inventory]:
    """Obtener inventario por ID de producto"""
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def get_inventory_by_id(db: Session, inventory_id: int) -> Optional[Inventory]:
    """Obtener inventario por su ID"""
    return db.query(Inventory).filter(Inventory.id == inventory_id).first()


def get_all_inventory(db: Session, skip: int = 0, limit: int = 100) -> List[Inventory]:
    """Obtener todos los registros de inventario"""
    return db.query(Inventory).offset(skip).limit(limit).all()


def create_or_update_inventory(db: Session, product_id: int, quantity: int) -> Inventory:
    """Crear o actualizar inventario para un producto"""
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"Producto con ID {product_id} no existe")
    
    inv = get_inventory_by_product(db, product_id)
    if inv:
        inv.quantity = quantity
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv
    else:
        inv = Inventory(product_id=product_id, quantity=quantity)
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv


def adjust_inventory(db: Session, product_id: int, delta: int) -> Inventory:
    """Ajustar inventario (sumar/restar cantidad)"""
    # Verificar que el producto existe
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f"Producto con ID {product_id} no existe")
    
    inv = get_inventory_by_product(db, product_id)
    if not inv:
        inv = Inventory(product_id=product_id, quantity=0)
        db.add(inv)
        db.commit()
        db.refresh(inv)

    inv.quantity += delta
    if inv.quantity < 0:
        inv.quantity = 0
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def delete_inventory(db: Session, product_id: int) -> bool:
    """Eliminar registro de inventario"""
    inv = get_inventory_by_product(db, product_id)
    if inv:
        db.delete(inv)
        db.commit()
        return True
    return False


def get_inventory_count(db: Session) -> int:
    """Contar total de registros de inventario"""
    return db.query(Inventory).count()


def get_low_stock(db: Session, threshold: int = 10) -> List[Inventory]:
    """Obtener productos con stock bajo"""
    return db.query(Inventory).filter(Inventory.quantity <= threshold).all()